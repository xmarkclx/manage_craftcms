from __future__ import annotations

import os
import subprocess
from pathlib import Path

from craftcms_management.common.env import read_env_file, required_env
from craftcms_management.common.files import safe_filename, timestamp
from craftcms_management.common.paths import BACKEND_ENV, BACKEND_ROOT, TMP_DIR
from craftcms_management.craftcms import (
    build_craft_db_backup_args,
    build_craft_db_restore_args,
)
from craftcms_management.database_dumps.mysql import (
    build_dump_command as build_mysql_dump_command,
)
from craftcms_management.database_dumps.postgres import (
    build_dump_command as build_postgres_dump_command,
)


def extract_local_db() -> Path:
    """Dump the local Craft CMS database configured in the backend .env to temp storage."""
    # Extract contents of local db based on thirst-2025-backend .env and put it in temp storage.
    # Returns the complete path of the SQL file.
    env = read_env_file(BACKEND_ENV)

    driver = required_env(env, "DB_DRIVER").lower()
    database = required_env(env, "DB_DATABASE")
    server = env.get("DB_SERVER") or "localhost"
    user = env.get("DB_USER") or None
    password = env.get("DB_PASSWORD") or None
    port = env.get("DB_PORT") or None

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TMP_DIR / f"{safe_filename(database, default='database')}-{timestamp()}.sql"

    if driver == "mysql":
        command = build_mysql_dump_command(server, user, port, database)
        command_env = os.environ.copy()
        if password is not None:
            command_env["MYSQL_PWD"] = password
    elif driver in {"pgsql", "postgres", "postgresql"}:
        command = build_postgres_dump_command(server, user, port, database)
        command_env = os.environ.copy()
        if password is not None:
            command_env["PGPASSWORD"] = password
    else:
        raise ValueError(f"Unsupported DB_DRIVER '{driver}'. Expected 'mysql' or 'pgsql'.")

    try:
        with output_path.open("w", encoding="utf-8") as output:
            subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                text=True,
                env=command_env,
                check=True,
            )
    except FileNotFoundError as exc:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"Required database dump command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        output_path.unlink(missing_ok=True)
        error = exc.stderr.strip() or f"{command[0]} exited with code {exc.returncode}"
        raise RuntimeError(f"Failed to dump local database: {error}") from exc

    return output_path.resolve()


def import_to_local_db(db_path: Path) -> None:
    """Import a database dump into the local Craft CMS database after backing it up."""
    db_path = db_path.resolve()
    if not db_path.is_file():
        raise FileNotFoundError(f"Database dump not found at {db_path}")

    for command in [
        build_craft_db_backup_args(),
        build_craft_db_restore_args(db_path),
    ]:
        try:
            subprocess.run(
                command,
                cwd=BACKEND_ROOT,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Required local Craft command not found: php") from exc
        except subprocess.CalledProcessError as exc:
            error = exc.stderr.strip() or f"php craft exited with code {exc.returncode}"
            raise RuntimeError(f"Failed to backup and import local database: {error}") from exc

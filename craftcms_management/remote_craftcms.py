from __future__ import annotations

import posixpath
import shlex
from pathlib import Path

from craftcms_management.common.files import safe_filename, timestamp
from craftcms_management.common.paths import TMP_DIR
from craftcms_management.craftcms import (
    build_craft_db_backup_shell_command,
    build_craft_db_restore_shell_command,
)
from craftcms_management.remote_ssh import (
    RemoteConfig,
    build_scp_command,
    build_ssh_command,
    in_remote_path,
    load_remote_config,
    run_command,
    run_command_to_file,
    run_optional_command,
)


def extract_production_db() -> Path:
    """Dump the production Craft CMS database to local temp storage without mutating production."""
    return _RemoteCraftCmsExtractor.from_env("PRODUCTION").extract_db()


def backup_production_db() -> None:
    """Back up the production Craft CMS database using Craft CLI on production."""
    _RemoteCraftCmsBackup.from_env("PRODUCTION").backup_db()


def import_to_staging_db(db_path: Path) -> None:
    """Import a local database dump into the staging Craft CMS database."""
    _RemoteCraftCmsImporter.from_env("STAGING").import_db(db_path)


def _remote_import_path(db_path: Path) -> str:
    """Build a unique remote temp path for a database import file."""
    filename = safe_filename(db_path.name, default="database.sql")
    return posixpath.join("/tmp", f"craft-import-{timestamp()}-{filename}")


def _build_remote_craft_db_restore_command(
    config: RemoteConfig,
    remote_path: str,
) -> str:
    """Build the remote shell command that backs up and restores the database."""
    return in_remote_path(
        config,
        [
            build_craft_db_backup_shell_command(),
            build_craft_db_restore_shell_command(remote_path),
        ],
    )


def _build_remote_craft_db_backup_command(config: RemoteConfig) -> str:
    """Build the remote shell command that backs up the Craft database."""
    return in_remote_path(config, [build_craft_db_backup_shell_command()])


def _build_remote_cleanup_command(remote_path: str) -> str:
    """Build the remote shell command that removes the copied dump file."""
    return f"rm -f {shlex.quote(remote_path)}"


def _build_remote_craft_db_dump_command(config: RemoteConfig) -> str:
    """Build a read-only remote shell command that streams a database dump."""
    return in_remote_path(
        config,
        [
            "set -a",
            ". ./.env",
            "set +a",
            (
                'case "$DB_DRIVER" in '
                'mysql) MYSQL_PWD="$DB_PASSWORD" mysqldump '
                "--single-transaction --quick --routines --triggers "
                '--host "${DB_SERVER:-localhost}" '
                '${DB_USER:+--user "$DB_USER"} '
                '${DB_PORT:+--port "$DB_PORT"} '
                '"$DB_DATABASE" ;; '
                'pgsql|postgres|postgresql) PGPASSWORD="$DB_PASSWORD" pg_dump '
                "--no-owner --no-privileges "
                '--host "${DB_SERVER:-localhost}" '
                '${DB_USER:+--username "$DB_USER"} '
                '${DB_PORT:+--port "$DB_PORT"} '
                '"$DB_DATABASE" ;; '
                '*) echo "Unsupported DB_DRIVER: $DB_DRIVER" >&2; exit 1 ;; '
                "esac"
            ),
        ],
    )


class _RemoteCraftCmsExtractor:
    """Extracts database dumps from a remote Craft CMS install."""

    def __init__(self, config: RemoteConfig, label: str):
        """Initialize the extractor with a remote SSH configuration."""
        self.config = config
        self.label = label

    @classmethod
    def from_env(cls, prefix: str) -> _RemoteCraftCmsExtractor:
        """Create an extractor from prefixed SSH settings."""
        return cls(load_remote_config(prefix=prefix), prefix.lower())

    def extract_db(self) -> Path:
        """Stream a remote database dump into local temp storage."""
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        output_path = TMP_DIR / f"{safe_filename(self.label, default='remote')}-{timestamp()}.sql"
        dump_command = _build_remote_craft_db_dump_command(self.config)
        ssh_dump_command = build_ssh_command(self.config, dump_command)

        run_command_to_file(
            ssh_dump_command,
            output_path,
            f"Failed to dump {self.label} database",
        )
        return output_path.resolve()


class _RemoteCraftCmsBackup:
    """Backs up a remote Craft CMS database in place."""

    def __init__(self, config: RemoteConfig):
        """Initialize the backup runner with a remote SSH configuration."""
        self.config = config

    @classmethod
    def from_env(cls, prefix: str) -> _RemoteCraftCmsBackup:
        """Create a backup runner from explicit prefixed SSH settings."""
        return cls(load_remote_config(prefix=prefix))

    def backup_db(self) -> None:
        """Run Craft's database backup command on the configured remote server."""
        backup_command = _build_remote_craft_db_backup_command(self.config)
        ssh_backup_command = build_ssh_command(self.config, backup_command)
        run_command(ssh_backup_command, "Failed to backup remote database")


class _RemoteCraftCmsImporter:
    """Imports database dumps into a remote Craft CMS install."""

    def __init__(self, config: RemoteConfig):
        """Initialize the importer with a remote SSH configuration."""
        self.config = config

    @classmethod
    def from_env(cls, prefix: str) -> _RemoteCraftCmsImporter:
        """Create an importer from explicit prefixed SSH settings."""
        return cls(load_remote_config(prefix=prefix))

    def import_db(self, db_path: Path) -> None:
        """Import a local database dump into the configured remote Craft CMS database."""
        db_path = db_path.resolve()
        if not db_path.is_file():
            raise FileNotFoundError(f"Database dump not found at {db_path}")

        remote_path = _remote_import_path(db_path)
        copied = False

        try:
            run_command(
                build_scp_command(db_path, self.config, remote_path),
                "Failed to copy database dump to remote server",
            )
            copied = True
            restore_command = _build_remote_craft_db_restore_command(
                self.config,
                remote_path,
            )
            ssh_restore_command = build_ssh_command(self.config, restore_command)
            run_command(
                ssh_restore_command,
                "Failed to backup and import remote database",
            )
        finally:
            if copied:
                run_optional_command(
                    build_ssh_command(
                        self.config,
                        _build_remote_cleanup_command(remote_path),
                    )
                )

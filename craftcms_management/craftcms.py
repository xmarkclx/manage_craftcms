from pathlib import Path
import shlex


def build_craft_db_backup_args() -> list[str]:
    """Build local argv for a Craft database backup."""
    return ["php", "craft", "db/backup", "--interactive=0"]


def build_craft_db_restore_args(db_path: Path) -> list[str]:
    """Build local argv for a Craft database restore."""
    return ["php", "craft", "db/restore", str(db_path), "--interactive=0"]


def build_craft_db_backup_shell_command() -> str:
    """Build a shell command for a Craft database backup."""
    return "php craft db/backup --interactive=0"


def build_craft_db_restore_shell_command(db_path: str) -> str:
    """Build a shell command for a Craft database restore."""
    return f"php craft db/restore {shlex.quote(db_path)} --interactive=0"

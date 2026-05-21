import unittest
from pathlib import Path

from craftcms_management.craftcms import (
    build_craft_db_backup_args,
    build_craft_db_backup_shell_command,
    build_craft_db_restore_args,
    build_craft_db_restore_shell_command,
)


class CraftCmsCommandTests(unittest.TestCase):
    """Tests for common Craft CMS command construction."""

    def test_builds_local_backup_args(self) -> None:
        """Build local argv for a database backup."""
        self.assertEqual(
            build_craft_db_backup_args(),
            ["php", "craft", "db/backup", "--interactive=0"],
        )

    def test_builds_local_restore_args(self) -> None:
        """Build local argv for a database restore."""
        self.assertEqual(
            build_craft_db_restore_args(Path("dump.sql")),
            ["php", "craft", "db/restore", "dump.sql", "--interactive=0"],
        )

    def test_builds_backup_shell_command(self) -> None:
        """Build a shell command for a database backup."""
        self.assertEqual(
            build_craft_db_backup_shell_command(),
            "php craft db/backup --interactive=0",
        )

    def test_builds_restore_shell_command(self) -> None:
        """Build a shell command for a database restore."""
        self.assertEqual(
            build_craft_db_restore_shell_command("/tmp/import file.sql"),
            "php craft db/restore '/tmp/import file.sql' --interactive=0",
        )


if __name__ == "__main__":
    unittest.main()

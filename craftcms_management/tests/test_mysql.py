import unittest

from craftcms_management.database_dumps.mysql import build_dump_command


class BuildMySqlDumpCommandTests(unittest.TestCase):
    """Tests for MySQL dump command construction."""

    def test_builds_full_command(self) -> None:
        """Include connection details and dump-safe defaults."""
        self.assertEqual(
            build_dump_command("localhost", "root", "3306", "craft"),
            [
                "mysqldump",
                "--single-transaction",
                "--quick",
                "--routines",
                "--triggers",
                "--host",
                "localhost",
                "--user",
                "root",
                "--port",
                "3306",
                "craft",
            ],
        )

    def test_omits_empty_optional_values(self) -> None:
        """Leave user and port flags out when they are not configured."""
        self.assertEqual(
            build_dump_command("localhost", None, None, "craft"),
            [
                "mysqldump",
                "--single-transaction",
                "--quick",
                "--routines",
                "--triggers",
                "--host",
                "localhost",
                "craft",
            ],
        )


if __name__ == "__main__":
    unittest.main()

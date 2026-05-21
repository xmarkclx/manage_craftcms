import unittest

from craftcms_management.database_dumps.postgres import build_dump_command


class BuildPostgresDumpCommandTests(unittest.TestCase):
    """Tests for PostgreSQL dump command construction."""

    def test_builds_full_command(self) -> None:
        """Include connection details and portable dump defaults."""
        self.assertEqual(
            build_dump_command("localhost", "postgres", "5432", "craft"),
            [
                "pg_dump",
                "--no-owner",
                "--no-privileges",
                "--host",
                "localhost",
                "--username",
                "postgres",
                "--port",
                "5432",
                "craft",
            ],
        )

    def test_omits_empty_optional_values(self) -> None:
        """Leave username and port flags out when they are not configured."""
        self.assertEqual(
            build_dump_command("localhost", None, None, "craft"),
            [
                "pg_dump",
                "--no-owner",
                "--no-privileges",
                "--host",
                "localhost",
                "craft",
            ],
        )


if __name__ == "__main__":
    unittest.main()

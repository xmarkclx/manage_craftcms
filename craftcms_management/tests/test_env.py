import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from craftcms_management.common.env import read_env_file, required_env


class ReadEnvFileTests(unittest.TestCase):
    """Tests for dotenv-style env parsing."""

    def test_reads_basic_key_value_pairs(self) -> None:
        """Parse unquoted key-value pairs."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("DB_DRIVER=mysql\nDB_DATABASE=craft\n", encoding="utf-8")

            self.assertEqual(
                read_env_file(env_path),
                {"DB_DRIVER": "mysql", "DB_DATABASE": "craft"},
            )

    def test_ignores_comments_blank_lines_and_lines_without_equals(self) -> None:
        """Skip non-env lines."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "\n# comment\nNOT_A_VALUE\nDB_USER=root\n",
                encoding="utf-8",
            )

            self.assertEqual(read_env_file(env_path), {"DB_USER": "root"})

    def test_strips_matching_quotes(self) -> None:
        """Strip matching single or double quotes around values."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                'DB_DRIVER="mysql"\nDB_USER=\'root\'\n',
                encoding="utf-8",
            )

            self.assertEqual(
                read_env_file(env_path),
                {"DB_DRIVER": "mysql", "DB_USER": "root"},
            )

    def test_preserves_inner_equals(self) -> None:
        """Keep equals signs inside values."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("DB_PASSWORD=abc=123\n", encoding="utf-8")

            self.assertEqual(read_env_file(env_path), {"DB_PASSWORD": "abc=123"})

    def test_missing_file_raises_file_not_found(self) -> None:
        """Raise a clear error when the env file is missing."""
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                read_env_file(Path(tmp) / ".env")


class RequiredEnvTests(unittest.TestCase):
    """Tests for required env validation."""

    def test_returns_present_value(self) -> None:
        """Return the configured value for a required key."""
        self.assertEqual(required_env({"DB_DATABASE": "craft"}, "DB_DATABASE"), "craft")

    def test_missing_value_raises_value_error(self) -> None:
        """Reject missing or empty required values."""
        with self.assertRaises(ValueError):
            required_env({"DB_DATABASE": ""}, "DB_DATABASE")


if __name__ == "__main__":
    unittest.main()

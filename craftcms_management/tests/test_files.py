import re
import unittest

from craftcms_management.common.files import safe_filename, timestamp


class SafeFilenameTests(unittest.TestCase):
    """Tests for safe filename formatting."""

    def test_replaces_unsafe_characters(self) -> None:
        """Convert unsafe filename characters to hyphens."""
        self.assertEqual(safe_filename("craft db: local/test"), "craft-db-local-test")

    def test_preserves_safe_characters(self) -> None:
        """Keep safe filename characters unchanged."""
        self.assertEqual(safe_filename("craft_db.local-2026"), "craft_db.local-2026")

    def test_returns_default_for_empty_result(self) -> None:
        """Use a default filename stem when no safe characters remain."""
        self.assertEqual(safe_filename("!!!"), "file")

    def test_returns_custom_default_for_empty_result(self) -> None:
        """Use a caller-provided fallback filename stem."""
        self.assertEqual(safe_filename("!!!", default="database"), "database")


class TimestampTests(unittest.TestCase):
    """Tests for filename timestamp formatting."""

    def test_returns_compact_timestamp(self) -> None:
        """Return a timestamp in YYYYMMDD-HHMMSS format."""
        self.assertRegex(timestamp(), re.compile(r"^\d{8}-\d{6}$"))


if __name__ == "__main__":
    unittest.main()

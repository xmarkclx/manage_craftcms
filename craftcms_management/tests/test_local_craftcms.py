import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from craftcms_management.local_craftcms import import_to_local_db


class ImportToLocalDbTests(unittest.TestCase):
    """Tests for importing database dumps locally."""

    @patch("craftcms_management.local_craftcms.subprocess.run")
    def test_backs_up_before_restoring_local_database(self, run) -> None:
        """Back up local DB before restoring the given dump."""
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "dump.sql"
            db_path.write_text("-- dump\n", encoding="utf-8")

            with patch("craftcms_management.local_craftcms.BACKEND_ROOT", Path("/backend")):
                import_to_local_db(db_path)

        resolved = str(db_path.resolve())
        self.assertEqual(
            run.call_args_list,
            [
                call(
                    ["php", "craft", "db/backup", "--interactive=0"],
                    cwd=Path("/backend"),
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                ),
                call(
                    ["php", "craft", "db/restore", resolved, "--interactive=0"],
                    cwd=Path("/backend"),
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                ),
            ],
        )

    def test_missing_dump_raises_file_not_found(self) -> None:
        """Reject missing local dump files."""
        with self.assertRaises(FileNotFoundError):
            import_to_local_db(Path("missing.sql"))


if __name__ == "__main__":
    unittest.main()

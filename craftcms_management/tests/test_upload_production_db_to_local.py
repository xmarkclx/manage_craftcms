import unittest
from pathlib import Path
from unittest.mock import patch

from upload_production_db_to_local import main


class UploadProductionDbToLocalTests(unittest.TestCase):
    """Tests for the production-to-local database script."""

    @patch("upload_production_db_to_local.success")
    @patch("upload_production_db_to_local.warning")
    @patch("upload_production_db_to_local.info")
    @patch("upload_production_db_to_local.import_to_local_db")
    @patch("upload_production_db_to_local.extract_production_db")
    def test_extracts_production_then_imports_locally(
        self,
        extract_production_db,
        import_to_local_db,
        _info,
        _warning,
        _success,
    ) -> None:
        """Import the downloaded production dump into the local database."""
        db_path = Path("/tmp/production.sql")
        extract_production_db.return_value = db_path

        main()

        extract_production_db.assert_called_once_with()
        import_to_local_db.assert_called_once_with(db_path)


if __name__ == "__main__":
    unittest.main()

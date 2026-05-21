import unittest
from unittest.mock import patch

from backup_production_db import main


class BackupProductionDbScriptTests(unittest.TestCase):
    """Tests for the production backup script."""

    @patch("backup_production_db.success")
    @patch("backup_production_db.warning")
    @patch("backup_production_db.info")
    @patch("backup_production_db.backup_production_db")
    def test_backs_up_production(
        self,
        backup_production_db,
        _info,
        _warning,
        _success,
    ) -> None:
        """Run the production backup workflow."""
        main()

        backup_production_db.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

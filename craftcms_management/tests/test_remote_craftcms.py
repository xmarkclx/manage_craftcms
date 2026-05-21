import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from craftcms_management.remote_craftcms import (
    _RemoteCraftCmsBackup,
    _RemoteCraftCmsExtractor,
    _RemoteCraftCmsImporter,
    _build_remote_craft_db_backup_command,
    _build_remote_craft_db_dump_command,
    _build_remote_craft_db_restore_command,
    backup_production_db,
    extract_production_db,
    import_to_staging_db,
)
from craftcms_management.remote_ssh import RemoteConfig


class RemoteCraftCmsCommandTests(unittest.TestCase):
    """Tests for remote Craft CMS command construction."""

    def test_builds_backup_before_restore_command(self) -> None:
        """Run a backup before restoring the uploaded dump."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        self.assertEqual(
            _build_remote_craft_db_restore_command(config, "/tmp/import.sql"),
            "cd /site/current && "
            "php craft db/backup --interactive=0 && "
            "php craft db/restore /tmp/import.sql --interactive=0",
        )

    def test_builds_backup_command(self) -> None:
        """Build a remote Craft database backup command."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        self.assertEqual(
            _build_remote_craft_db_backup_command(config),
            "cd /site/current && php craft db/backup --interactive=0",
        )

    def test_builds_read_only_dump_command(self) -> None:
        """Stream a database dump without writing to the remote server."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        command = _build_remote_craft_db_dump_command(config)

        self.assertIn("cd /site/current", command)
        self.assertIn(". ./.env", command)
        self.assertIn("mysqldump", command)
        self.assertIn("pg_dump", command)
        self.assertNotIn("db/backup", command)
        self.assertNotIn("db/restore", command)
        self.assertNotIn("scp", command)


class ImportToRemoteDbTests(unittest.TestCase):
    """Tests for the remote import workflow."""

    @patch("craftcms_management.remote_craftcms._remote_import_path")
    @patch("craftcms_management.remote_ssh.subprocess.run")
    def test_copies_backs_up_restores_and_cleans_up(self, run, import_path) -> None:
        """Copy the dump, back up the remote DB, restore it, then clean up."""
        config = RemoteConfig("forge", "example.com", "/site/current")
        import_path.return_value = "/tmp/import.sql"

        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "local.sql"
            db_path.write_text("-- dump\n", encoding="utf-8")

            _RemoteCraftCmsImporter(config).import_db(db_path)

        local_path = str(db_path.resolve())
        restore = (
            "cd /site/current && "
            "php craft db/backup --interactive=0 && "
            "php craft db/restore /tmp/import.sql --interactive=0"
        )
        self.assertEqual(
            run.call_args_list,
            [
                call(
                    ["scp", local_path, "forge@example.com:/tmp/import.sql"],
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                ),
                call(
                    ["ssh", "forge@example.com", restore],
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                ),
                call(
                    ["ssh", "forge@example.com", "rm -f /tmp/import.sql"],
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                ),
            ],
        )

    def test_missing_dump_raises_file_not_found(self) -> None:
        """Reject missing local dump files."""
        importer = _RemoteCraftCmsImporter(
            RemoteConfig("forge", "example.com", "/site/current")
        )

        with self.assertRaises(FileNotFoundError):
            importer.import_db(Path("missing.sql"))

    @patch("craftcms_management.remote_craftcms._RemoteCraftCmsImporter")
    def test_public_import_uses_staging_config(self, importer_class) -> None:
        """Expose import_to_staging_db as an explicit staging import function."""
        importer = importer_class.from_env.return_value

        import_to_staging_db(Path("local.sql"))

        importer_class.from_env.assert_called_once_with("STAGING")
        importer.import_db.assert_called_once_with(Path("local.sql"))


class BackupProductionDbTests(unittest.TestCase):
    """Tests for the production backup workflow."""

    @patch("craftcms_management.remote_ssh.subprocess.run")
    def test_runs_remote_craft_backup_command(self, run) -> None:
        """Back up the remote database with Craft CLI."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        _RemoteCraftCmsBackup(config).backup_db()

        self.assertEqual(
            run.call_args,
            call(
                [
                    "ssh",
                    "forge@example.com",
                    "cd /site/current && php craft db/backup --interactive=0",
                ],
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            ),
        )

    @patch("craftcms_management.remote_craftcms._RemoteCraftCmsBackup")
    def test_public_backup_uses_production_config(self, backup_class) -> None:
        """Expose production backup with the production SSH prefix."""
        backup = backup_class.from_env.return_value

        backup_production_db()

        backup_class.from_env.assert_called_once_with("PRODUCTION")
        backup.backup_db.assert_called_once_with()


class ExtractProductionDbTests(unittest.TestCase):
    """Tests for the remote production export workflow."""

    @patch("craftcms_management.remote_craftcms.timestamp")
    @patch("craftcms_management.remote_ssh.subprocess.run")
    def test_streams_remote_dump_to_local_file_without_remote_writes(self, run, timestamp) -> None:
        """Extract the remote database through SSH stdout."""
        timestamp.return_value = "20260520-130000"
        config = RemoteConfig("forge", "example.com", "/site/current")

        with TemporaryDirectory() as tmp:
            with patch("craftcms_management.remote_craftcms.TMP_DIR", Path(tmp)):
                db_path = _RemoteCraftCmsExtractor(config, "production").extract_db()

        self.assertEqual(db_path.name, "production-20260520-130000.sql")
        self.assertEqual(run.call_args.args[0][0], "ssh")
        self.assertEqual(run.call_args.args[0][1], "forge@example.com")
        self.assertIn("mysqldump", run.call_args.args[0][2])
        self.assertIn("pg_dump", run.call_args.args[0][2])
        self.assertEqual(run.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(run.call_args.kwargs["text"])
        self.assertTrue(run.call_args.kwargs["check"])

    @patch("craftcms_management.remote_craftcms._RemoteCraftCmsExtractor")
    def test_public_extract_uses_production_config(self, extractor_class) -> None:
        """Expose production extraction with the production SSH prefix."""
        extractor = extractor_class.from_env.return_value

        extract_production_db()

        extractor_class.from_env.assert_called_once_with("PRODUCTION")
        extractor.extract_db.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

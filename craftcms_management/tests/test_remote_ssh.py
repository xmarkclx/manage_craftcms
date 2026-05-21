import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from craftcms_management.remote_ssh import (
    RemoteConfig,
    build_scp_command,
    build_ssh_command,
    in_remote_path,
    load_remote_config,
    run_command,
    run_command_to_file,
)


class LoadRemoteConfigTests(unittest.TestCase):
    """Tests for remote SSH configuration loading."""

    def test_loads_required_ssh_values(self) -> None:
        """Read SSH settings from a dotenv file."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "STAGING_SSH_USERNAME=forge\n"
                "STAGING_SSH_HOST=example.com\n"
                "STAGING_SSH_PATH=/site/current\n",
                encoding="utf-8",
            )

            config = load_remote_config("STAGING", env_path)

            self.assertEqual(config.username, "forge")
            self.assertEqual(config.host, "example.com")
            self.assertEqual(config.path, "/site/current")
            self.assertEqual(config.target, "forge@example.com")

    def test_missing_ssh_value_raises_value_error(self) -> None:
        """Reject env files without complete SSH settings."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "STAGING_SSH_USERNAME=forge\nSTAGING_SSH_HOST=example.com\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_remote_config("STAGING", env_path)

    def test_ignores_unprefixed_ssh_values(self) -> None:
        """Require staging-prefixed SSH settings."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "SSH_USERNAME=forge\nSSH_HOST=example.com\nSSH_PATH=/site/current\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_remote_config("STAGING", env_path)

    def test_loads_custom_prefixed_ssh_values(self) -> None:
        """Support other remote environment prefixes."""
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "PRODUCTION_SSH_USERNAME=forge\n"
                "PRODUCTION_SSH_HOST=example.com\n"
                "PRODUCTION_SSH_PATH=/site/current\n",
                encoding="utf-8",
            )

            config = load_remote_config("PRODUCTION", env_path)

            self.assertEqual(config.target, "forge@example.com")
            self.assertEqual(config.path, "/site/current")


class RemoteSshCommandTests(unittest.TestCase):
    """Tests for SSH command construction."""

    def test_builds_scp_command(self) -> None:
        """Copy a file to the configured SSH target."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        self.assertEqual(
            build_scp_command(Path("local.sql"), config, "/tmp/import.sql"),
            ["scp", "local.sql", "forge@example.com:/tmp/import.sql"],
        )

    def test_builds_command_in_remote_path(self) -> None:
        """Prefix commands with a change into the configured remote path."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        self.assertEqual(
            in_remote_path(config, ["php craft foo", "php craft bar"]),
            "cd /site/current && php craft foo && php craft bar",
        )

    def test_builds_ssh_command(self) -> None:
        """Run the remote command over SSH."""
        config = RemoteConfig("forge", "example.com", "/site/current")

        self.assertEqual(
            build_ssh_command(config, "php craft db/backup --interactive=0"),
            ["ssh", "forge@example.com", "php craft db/backup --interactive=0"],
        )


class RunCommandTests(unittest.TestCase):
    """Tests for subprocess error handling."""

    @patch("craftcms_management.remote_ssh.subprocess.run")
    def test_raises_runtime_error_with_stderr(self, run) -> None:
        """Include stderr when a command fails."""
        run.side_effect = subprocess.CalledProcessError(1, ["ssh"], stderr="failed")

        with self.assertRaisesRegex(RuntimeError, "Import failed: failed"):
            run_command(["ssh"], "Import failed")

    @patch("craftcms_management.remote_ssh.subprocess.run")
    def test_writes_command_stdout_to_file(self, run) -> None:
        """Write command output to the given file."""
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "dump.sql"

            run_command_to_file(["ssh", "example.com", "dump"], output_path, "Dump failed")

        self.assertEqual(run.call_args.args[0], ["ssh", "example.com", "dump"])
        self.assertEqual(run.call_args.kwargs["stderr"], subprocess.PIPE)
        self.assertTrue(run.call_args.kwargs["text"])
        self.assertTrue(run.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()

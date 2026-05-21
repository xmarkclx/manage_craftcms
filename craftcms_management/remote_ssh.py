from __future__ import annotations

from dataclasses import dataclass
import shlex
from pathlib import Path
import subprocess

from craftcms_management.common.env import read_env_file, required_env
from craftcms_management.common.paths import SCRIPTS_ENV


@dataclass(frozen=True)
class RemoteConfig:
    """SSH configuration for remote commands."""

    username: str
    host: str
    path: str

    @property
    def target(self) -> str:
        """Return the SSH target in user@host format."""
        return f"{self.username}@{self.host}"


def load_remote_config(prefix: str, env_file: Path = SCRIPTS_ENV) -> RemoteConfig:
    """Load required prefixed SSH settings from a dotenv file."""
    env = read_env_file(env_file)
    key_prefix = f"{prefix}_"
    return RemoteConfig(
        username=required_env(env, f"{key_prefix}SSH_USERNAME"),
        host=required_env(env, f"{key_prefix}SSH_HOST"),
        path=required_env(env, f"{key_prefix}SSH_PATH"),
    )


def build_scp_command(db_path: Path, config: RemoteConfig, remote_path: str) -> list[str]:
    """Build the command that copies a file to the remote server."""
    return ["scp", str(db_path), f"{config.target}:{remote_path}"]


def in_remote_path(config: RemoteConfig, commands: list[str]) -> str:
    """Build a shell command that runs commands from the configured remote path."""
    return " && ".join([f"cd {shlex.quote(config.path)}", *commands])


def build_ssh_command(config: RemoteConfig, remote_command: str) -> list[str]:
    """Build an SSH command for the configured remote host."""
    return ["ssh", config.target, remote_command]


def run_command(command: list[str], failure_message: str) -> None:
    """Run a command and raise a runtime error with stderr on failure."""
    try:
        subprocess.run(command, stderr=subprocess.PIPE, text=True, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        error = exc.stderr.strip() or f"{command[0]} exited with code {exc.returncode}"
        raise RuntimeError(f"{failure_message}: {error}") from exc


def run_command_to_file(command: list[str], output_path: Path, failure_message: str) -> None:
    """Run a command and write stdout to a file."""
    try:
        with output_path.open("w", encoding="utf-8") as output:
            subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
    except FileNotFoundError as exc:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"Required command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        output_path.unlink(missing_ok=True)
        error = exc.stderr.strip() or f"{command[0]} exited with code {exc.returncode}"
        raise RuntimeError(f"{failure_message}: {error}") from exc


def run_optional_command(command: list[str]) -> None:
    """Run a best-effort command and ignore missing executables."""
    try:
        subprocess.run(command, stderr=subprocess.PIPE, text=True, check=False)
    except FileNotFoundError:
        pass

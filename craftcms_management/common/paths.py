from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir

from craftcms_management.common.env import read_env_file, required_env


SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ENV = SCRIPTS_ROOT / ".env"


@dataclass(frozen=True)
class PathConfig:
    """Resolved filesystem paths used by the agency management scripts."""

    repo_root: Path
    backend_root: Path
    backend_env: Path
    tmp_dir: Path


def env_path(value: str, base_dir: Path) -> Path:
    """Resolve a dotenv path value relative to its env file directory."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def load_path_config(env_file: Path = SCRIPTS_ENV) -> PathConfig:
    """Load path configuration from a dotenv file."""
    env = read_env_file(env_file)
    backend_root = env_path(required_env(env, "BACKEND_ROOT"), env_file.parent)

    return PathConfig(
        repo_root=backend_root.parent,
        backend_root=backend_root,
        backend_env=backend_root / ".env",
        tmp_dir=Path(gettempdir()).resolve(),
    )


_paths = load_path_config()

REPO_ROOT = _paths.repo_root
BACKEND_ROOT = _paths.backend_root
BACKEND_ENV = _paths.backend_env
TMP_DIR = _paths.tmp_dir

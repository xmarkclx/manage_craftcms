from pathlib import Path


def read_env_file(path: Path) -> dict[str, str]:
    """Read a dotenv-style file into a key-value mapping."""
    if not path.exists():
        raise FileNotFoundError(f"Env file not found at {path}")

    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        env[key.strip()] = value

    return env


def required_env(env: dict[str, str], key: str) -> str:
    """Return a required environment value or raise a clear validation error."""
    value = env.get(key)
    if not value:
        raise ValueError(f"Missing required env value: {key}")
    return value

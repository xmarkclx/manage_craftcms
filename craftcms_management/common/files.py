import re
from datetime import datetime


def safe_filename(value: str, default: str = "file") -> str:
    """Convert a value into a safe filename stem."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return safe or default


def timestamp() -> str:
    """Return a compact local timestamp suitable for filenames."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")

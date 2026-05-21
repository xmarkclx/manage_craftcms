INFO_COLOR = "\033[34m"
WARNING_COLOR = "\033[33m"
ERROR_COLOR = "\033[31m"
SUCCESS_COLOR = "\033[32m"
RESET = "\033[0m"

INFO_ICON = "ℹ️"
WARNING_ICON = "⚠️"
ERROR_ICON = "❌"
SUCCESS_ICON = "✅"


def status(icon: str, color: str, message: str) -> None:
    """Print a colored status message."""
    print(f"{color}{icon} {message}{RESET}")


def info(message: str) -> None:
    """Print an informational status message."""
    status(INFO_ICON, INFO_COLOR, message)


def warning(message: str) -> None:
    """Print a warning status message."""
    status(WARNING_ICON, WARNING_COLOR, message)


def error(message: str) -> None:
    """Print an error status message."""
    status(ERROR_ICON, ERROR_COLOR, message)


def success(message: str) -> None:
    """Print a successful status message."""
    status(SUCCESS_ICON, SUCCESS_COLOR, message)

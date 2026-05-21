import unittest
from io import StringIO
from unittest.mock import patch

from craftcms_management.common.cli import (
    ERROR_COLOR,
    ERROR_ICON,
    INFO_COLOR,
    INFO_ICON,
    RESET,
    SUCCESS_COLOR,
    SUCCESS_ICON,
    WARNING_COLOR,
    WARNING_ICON,
    error,
    info,
    status,
    success,
    warning,
)


class StatusTests(unittest.TestCase):
    """Tests for CLI status output."""

    def test_prints_colored_status_message(self) -> None:
        """Wrap status messages in ANSI color codes."""
        output = StringIO()

        with patch("sys.stdout", output):
            status(SUCCESS_ICON, SUCCESS_COLOR, "Done")

        self.assertEqual(output.getvalue(), f"{SUCCESS_COLOR}{SUCCESS_ICON} Done{RESET}\n")

    def test_prints_standard_status_levels(self) -> None:
        """Use standardized icons and colors for each status level."""
        output = StringIO()

        with patch("sys.stdout", output):
            info("Info")
            warning("Warning")
            error("Error")
            success("Success")

        self.assertEqual(
            output.getvalue(),
            f"{INFO_COLOR}{INFO_ICON} Info{RESET}\n"
            f"{WARNING_COLOR}{WARNING_ICON} Warning{RESET}\n"
            f"{ERROR_COLOR}{ERROR_ICON} Error{RESET}\n"
            f"{SUCCESS_COLOR}{SUCCESS_ICON} Success{RESET}\n",
        )


if __name__ == "__main__":
    unittest.main()

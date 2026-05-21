#!/usr/bin/env -S uv run python3

from craftcms_management.common.cli import info, success, warning
from craftcms_management.remote_craftcms import backup_production_db


def main() -> None:
    """Back up the production Craft CMS database using Craft CLI."""
    info("Starting production database backup")
    warning("Production backup only runs Craft's db/backup command; no restore will run")
    backup_production_db()
    success("Production database backup complete")


if __name__ == "__main__":
    main()

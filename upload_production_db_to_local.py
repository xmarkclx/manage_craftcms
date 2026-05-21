#!/usr/bin/env -S uv run python3

from craftcms_management.common.cli import info, success, warning
from craftcms_management.local_craftcms import import_to_local_db
from craftcms_management.remote_craftcms import extract_production_db


def main() -> None:
    """Download the production Craft CMS database dump and import it locally."""
    info("Starting read-only production database export")

    warning("Production will only be read from; no backup, restore, or remote file write will run")
    db_path = extract_production_db()
    success(f"Production database dump ready: {db_path}")

    warning("Backing up local database and importing production dump...")
    import_to_local_db(db_path)
    success("Local database import complete")


if __name__ == "__main__":
    main()

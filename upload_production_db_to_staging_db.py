#!/usr/bin/env -S uv run python3

from craftcms_management.common.cli import info, success, warning
from craftcms_management.remote_craftcms import extract_production_db, import_to_staging_db


def main() -> None:
    """Upload the production Craft CMS database dump to staging."""
    info("Starting production database upload to staging")

    warning("Production will only be read from; no backup, restore, or remote file write will run")
    db_path = extract_production_db()
    success(f"Production database dump ready: {db_path}")

    warning("Backing up staging and importing production dump...")
    import_to_staging_db(db_path)
    success("Staging database import complete")


if __name__ == "__main__":
    main()

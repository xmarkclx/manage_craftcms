#!/usr/bin/env -S uv run python3

from craftcms_management.common import cli
from craftcms_management.local_craftcms import extract_local_db
from craftcms_management.remote_craftcms import import_to_staging_db


def main() -> None:
    """Upload the local Craft CMS database dump to staging."""
    cli.info("Starting local database upload to staging")

    cli.info("Exporting local Craft CMS database...")
    db_path = extract_local_db()
    cli.success(f"Local database dump ready: {db_path}")

    cli.warning("Backing up staging and importing local dump...")
    import_to_staging_db(db_path)
    cli.success("Staging database import complete")


if __name__ == "__main__":
    main()

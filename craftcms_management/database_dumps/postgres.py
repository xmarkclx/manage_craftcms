def build_dump_command(
    server: str,
    user: str | None,
    port: str | None,
    database: str,
) -> list[str]:
    """Build a pg_dump command for the configured PostgreSQL database."""
    command = ["pg_dump", "--no-owner", "--no-privileges", "--host", server]
    if user:
        command.extend(["--username", user])
    if port:
        command.extend(["--port", port])
    command.append(database)
    return command

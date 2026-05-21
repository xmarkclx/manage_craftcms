def build_dump_command(
    server: str,
    user: str | None,
    port: str | None,
    database: str,
) -> list[str]:
    """Build a mysqldump command for the configured MySQL database."""
    command = [
        "mysqldump",
        "--single-transaction",
        "--quick",
        "--routines",
        "--triggers",
        "--host",
        server,
    ]
    if user:
        command.extend(["--user", user])
    if port:
        command.extend(["--port", port])
    command.append(database)
    return command

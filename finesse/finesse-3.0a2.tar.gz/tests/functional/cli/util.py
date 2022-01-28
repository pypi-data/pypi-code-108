def sanitized_output(cli_result):
    """Return the CLI output with leading and trailing whitespace removed."""
    return "\n".join([line.strip() for line in cli_result.output.splitlines()])

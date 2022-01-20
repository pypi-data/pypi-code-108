from json import dumps, loads
from sys import stderr

import click

from common.rpc.slack import export_channel, list_conversations, list_users


def decorate_exporter(f):
    for decorator in reversed(
        [
            click.option("--course", prompt=True, required=True),
            click.option("--include-dms/--exclude-dms", prompt=True, required=True),
            click.option("--load-from", type=click.File("r")),
            click.option("--out", type=click.File("w"), prompt=True, required=True),
        ]
    ):
        f = decorator(f)
    return f


@decorate_exporter
def slack_export(course, include_dms, load_from, out):
    """Export all the data from an associated Slack workspace.

    Outputs a JSON into OUT. Specify LOAD-FROM to merge with the output of a previous JSON to bypass
    the 10,000 message history.
    """
    try:
        conversations = list_conversations(course=course, include_dms=include_dms)
    except Exception as _:
        click.echo(
            "Unable to list conversations in Slack. "
            f"Have you added your workspace to https://auth.cs61a.org "
            "and installed the bot at https://slack.cs61a.org/register/{course}?",
            err=True,
        )
        return

    print("Exporting Channels:", [c["name"] for c in conversations])
    click.confirm("Confirm export?", abort=True)

    export = {}

    if load_from:
        export = loads(load_from.read())

    export["_users"] = list_users(course=course)

    for c in conversations:
        print(f"Exporting {c['name']}: ", end="", file=stderr, flush=True)
        messages = (
            {m["ts"]: m for m in export[c["id"]]["messages"]}
            if c["id"] in export
            else {}
        )
        new_messages = export_channel(course=course, channel_id=c["id"])
        print(len(new_messages), "messages downloaded", end="", file=stderr)
        for m in new_messages:
            messages[m["ts"]] = m
        print(",", len(messages), "total messages ", file=stderr)
        export[c["id"]] = dict(
            name=c["name"], messages=sorted(messages.values(), key=lambda m: m["ts"])
        )
    out.write(dumps(export))

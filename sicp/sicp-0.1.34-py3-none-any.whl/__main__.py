import sys
from warnings import warn

import click
import os

from sicp.build import build
from sicp.clone import clone
from sicp.slack import slack
from sicp.venv import venv
from sicp.pr import pr
from sicp.auth import auth
from sicp.send import send
from sicp.slack_export import decorate_exporter, slack_export

from common.rpc.auth_utils import set_token_path


@click.group()
def cli():
    """
    This is an experimental general-purpose 61A task runner.
    """
    set_token_path(f"{os.path.expanduser('~')}/.sicp_token")


cli.add_command(clone)
cli.add_command(build)
cli.add_command(venv)
cli.add_command(pr)
cli.add_command(auth)
cli.add_command(send)
cli.add_command(click.command(hidden=True)(decorate_exporter(slack_export)))
cli.add_command(slack)

if sys.version_info[0] == 3 and sys.version_info[1] < 8:
    warn("sicp may not work properly on versions of Python before 3.8")

if __name__ == "__main__":
    cli()

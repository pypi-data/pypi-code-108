import functools
import logging
import sys
import os

import click

from . import __version__
from .core import show_variables_as_tree

LOG_LEVELS = {
    "NOTSET": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logger = logging.getLogger(__name__)


def require_gitlab_auth_env_variables(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        ctx = click.get_current_context()

        GITLAB_URL = os.environ.get("GITLAB_URL")
        GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")

        if GITLAB_URL is None:
            logger.error("Missing 'GITLAB_URL' environment variable.")
            sys.exit(1)

        if GITLAB_TOKEN is None:
            logger.error("Missing 'GITLAB_TOKEN' environment variable.")
            sys.exit(1)

        ctx.obj["GITLAB_URL"] = GITLAB_URL
        ctx.obj["GITLAB_TOKEN"] = GITLAB_TOKEN
        return func(*args, **kwargs)

    return wrapper_decorator


@click.group()
@click.option("--log-level", default="ERROR")
@click.pass_context
def main(ctx, log_level):
    ctx.ensure_object(dict)

    if not log_level in LOG_LEVELS:
        logger.error(
            "Please use valud '--log-level' argument, one of them: '{}'".format(
                ", ".join(LOG_LEVELS.keys())
            )
        )
        sys.exit(1)

    logging.basicConfig(level=LOG_LEVELS.get(log_level))


@main.command("version")
def version_cmd():
    click.echo(f"gitlab-ci-cd-variables-tree: {__version__}")


@main.command("show")
@click.pass_context
@click.option("--gitlab-group-id", required=True, help="Gitlab Group ID")
@require_gitlab_auth_env_variables
def show_cmd(ctx, gitlab_group_id):
    GITLAB_URL = ctx.obj.get("GITLAB_URL")
    GITLAB_TOKEN = ctx.obj.get("GITLAB_TOKEN")

    show_variables_as_tree(
        gitlab_url=GITLAB_URL,
        gitlab_token=GITLAB_TOKEN,
        gitlab_group_id=gitlab_group_id,
    )

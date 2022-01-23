""" CLI. """
import logging
import sys
import os

import click

from nerddiary import __version__
from nerddiary.log import configure_logger
from nerddiary.bots.tgbot.bot import main as bot_entry


def version_msg() -> str:
    """Return the version, location and Python powering it."""
    python_version = sys.version
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    message = "Migrelyzer %(version)s from {} (Python {})"
    return message.format(location, python_version)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-V", "--version", message=version_msg())
@click.option(
    "-v", "--verbose", is_flag=True, help="Force all log levels to debug", default=False
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Whether to output interactive prompts",
    default=False,
)
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="File to be used for logging",
)
@click.option(
    "--log-level",
    type=click.Choice(
        [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        case_sensitive=False,
    ),
    help="Log level",
    default="INFO",
    show_default=True,
)
def cli(
    log_file: str,
    log_level: str,
    verbose: bool,
    interactive: bool,
) -> None:
    """Main entry point"""

    logger = configure_logger(
        log_level=log_level if not verbose else "DEBUG", log_file=log_file
    )

    logger.debug("Init cli. Succesful connection to G SHeet API")


@cli.command()
@click.pass_context
@click.option("--token", "-tt", help="Telegram BOT token")
def bot(ctx: click.Context, token: str) -> None:

    logger = logging.getLogger("nerddiary.bot")
    interactive = ctx.parent.params["interactive"]  # type: ignore
    config_file = ctx.parent.params["config_file"]

    if not config_file:
        if interactive:
            click.echo("Please provide a valid config file")
        sys.exit(1)

    # LOAD TOKEN
    if not token:
        logger.error(
            "Bot Token must be set in NERDDIARY_BOT_TOKEN environment var or provided via -tt option"
        )

        if interactive:
            click.echo(
                click.style(
                    "Bot Token must be set in NERDDIARY_BOT_TOKEN environment var or provided via -tt option",
                    fg="red",
                )
            )

        sys.exit(1)

    if interactive:
        click.echo(click.style("Starting the bot!", fg="green"))

    api_wrapper = ctx.obj

    bot_entry(
        config_file=config_file,
        gsheet_api_wrapper=api_wrapper,
        bot_token=token,
    )

    logger.info("Bot stopping")


if __name__ == "__main__":
    cli(auto_envvar_prefix="NERDDIARY")

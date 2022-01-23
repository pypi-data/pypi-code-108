from .run import run
from .project import project
import emoji
import click
import logging
import sys
from ..config import set_config

logger = logging.getLogger(__name__)
logger.disabled = True
logger.setLevel(logging.ERROR)
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)


@click.group()
@click.option('--config_file_path', '-c', default=None)
def bdk(config_file_path):
    set_config(config_file_path=config_file_path)
    click.secho(emoji.emojize('Welcome to badook cli :falafel:',
                use_aliases=True), fg='green', bold=True)


bdk.add_command(run)
bdk.add_command(project)


def main():
    bdk(None)


if __name__ == "__main__":
    main()

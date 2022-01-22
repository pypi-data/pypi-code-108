import signal
import sys
import logging
import click
from . import version
from .model import model
from .job import job
from .project import project
from .auth import login
from .container import container
from .ds import data
from .checkpoint import checkpoint
from .service import service
from .work import work
from .info import info


def sigint_handler(signum, frame):
    logging.debug("signal {}, {}".format(signum, frame))
    click.echo()
    sys.exit()


signal.signal(signal.SIGINT, sigint_handler)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.version_option(version=version.__version__)
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

cli.add_command(login)
cli.add_command(data)
cli.add_command(model)
#cli.add_command(train)
cli.add_command(job)
cli.add_command(project)
cli.add_command(container)
cli.add_command(checkpoint)
cli.add_command(service)
cli.add_command(work)
cli.add_command(info)


if __name__ == '__main__':
    cli()

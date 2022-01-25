# -*- encoding: utf-8 -*-

import click
import os
from clspy.utils import pipguess


@click.option('--pypi',
              '-p',
              default='https://pypi.org/simple',
              help='Use pypi source, default: https://pypi.org/simple')
@click.command(context_settings=dict(
    allow_extra_args=True,
    ignore_unknown_options=True,
),
    help="CLSLQ upgrade")
def upgrade(pypi):
    if pypi:
        click.secho("PYPI:{}.".format(pypi), fg='green')
        os.system("{} install clslq --upgrade -i {}".format(pipguess(), pypi))
    


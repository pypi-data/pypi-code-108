#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._cli._bookmark_cli import bookmark
from dxi._cli._branch_cli import branch
from dxi._cli._config_cli import config
from dxi._cli._container_cli import container
from dxi._cli._database_cli import database
from dxi._cli._environment_cli import environment
from dxi._cli._snapshot_cli import snapshot
from dxi._cli._template_cli import template
from dxi._cli._group_cli import group
from dxi._cli._user_cli import user
from dxi._version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="dxi")
def dxi():
    """
    dxi is a command line interface to trigger Delphix operations and to
    integrate Delphix into automated workflows.
    """


# Adding snapshot as sub-group-command of dxi
dxi.add_command(snapshot)

# Adding snapshot as sub-group-command of dxi
dxi.add_command(database)

# Adding environment as sub-group-command of dxi
dxi.add_command(environment)

# Adding branch as sub-group-command of dxi
dxi.add_command(branch)

# Adding bookmark as sub-group-command of dxi
dxi.add_command(bookmark)

# Adding container as sub-group-command of dxi
dxi.add_command(container)

# Adding template as sub-group-command of dxi
dxi.add_command(template)

# Adding config as sub-group-command of dxi
dxi.add_command(config)

# Adding group as sub-group-command of dxi
dxi.add_command(group)

# Adding user as sub-group-command of dxi
dxi.add_command(user)

if __name__ == "__main__":
    dxi()

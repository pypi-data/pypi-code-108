import os
import click
from jiracmd.cli.worklog import worklog_cli
from jiracmd.cli.issue import issue_cli

@click.group()
@click.version_option()
def cli():
    pass

cli.add_command(worklog_cli)
cli.add_command(issue_cli)

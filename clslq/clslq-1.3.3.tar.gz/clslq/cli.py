# -*- encoding: utf-8 -*-
'''
cli

click.group(name='main')

'''
import os
import click
from click.termui import prompt
from clslq.cli_clslq_pip import pip
from clslq.cli_clslq_venv import venv
from clslq.cli_clslq_notion import notion
from clslq.cli_clslq_upgrade import upgrade
from clslq.cli_notion_backup import notion_backup
from clslq.cli_git import git

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(name="main", context_settings=CONTEXT_SETTINGS)
@click.version_option(message='%(prog)s-%(version)s')
def main():
    """
    CLSLQ is a python library and command toolsets of Connard.
    Most of the contents are written in progress of python learning.
    CLSLQ include some quick-start python programming functions, wrappers and tools.
    For more information, please contact [lovelacelee@gmail.com].
    Documents available on https://clslq.readthedocs.io/.
    MIT License Copyright (c) Connard Lee.
    """
    pass


main.add_command(pip, name='pip')
main.add_command(venv, name='venv')
main.add_command(notion, name='notion')
main.add_command(upgrade, name='upgrade')
main.add_command(notion_backup, name='notion_backup')
main.add_command(git, name='git')

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import sys

import click

from pspipe import database, tasks
from pspipe import __version__

from .psdb import load_settings


tasks_help = '\n'.join([f'  {name.ljust(17)}{desc}' for name, desc in tasks.get_all_tasks_descriptions().items()])


@click.command(epilog='\b\nAvailable tasks:\n' + tasks_help)
@click.version_option(__version__)
@click.argument('tasks_str', metavar='TASKS')
@click.argument('settings_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('obs_ids')
@click.argument('config_modifier', nargs=-1)
def main(tasks_str, settings_file, obs_ids, config_modifier):
    ''' End-to-end power spectra generation pipeline

        \b
        TASKS: Tasks to execute, comma separated
        CONFIG: Configuration file
        OBS_IDS: Obs IDs to process, comma separated with bash-type wildcards support
        CONFIG_MODIFIERS: Optional configuration modifiers, of the form key=value '''

    s = load_settings(settings_file, config_modifier)

    all_tasks = tasks.get_all_tasks()

    for task_name in tasks_str.split(','):
        if task_name not in all_tasks:
            print(f'Error: task {task_name} does not exist.')
            sys.exit(1)

    obs_ids_set = database.Database(s).filter_obs_ids(obs_ids)

    if not obs_ids:
        print(f'Error: No obs_ids matching {obs_ids} in database.')
        sys.exit(1)

    for task_name in tasks_str.split(','):
        obs_ids_set = all_tasks[task_name](s).run(obs_ids_set)
        if not obs_ids_set:
            print('\nError: no obs_id to process.')
            sys.exit(1)

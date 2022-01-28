#!/usr/bin/env python

import os
import json

import click

from libpipe import worker
from libpipe import __version__


t_file = click.Path(exists=True, dir_okay=False)


@click.group()
@click.version_option(__version__)
def main():
    ''' Nodes utilities ...'''


@main.command('run_all')
@click.argument('cmd_list', type=t_file)
@click.option('--nodes_string', '-n', help='Range of nodes to use', type=str, default='localhost')
@click.option('--max_concurrent', '-m', help='Maximum concurrent tasks on a node', type=int, default=5)
@click.option('--env_file', '-e', help='Environment source file', type=t_file)
@click.option('--dry_run', '-d', help='Dry run, only print commands', is_flag=True)
@click.option('--log_file', help='Log output to log_file', type=str, default=None)
def run_all(cmd_list, nodes_string, max_concurrent, env_file, dry_run, log_file):
    ''' Run all command listed in the file CMD_LIST.'''
    pool = worker.get_worker_pool('Run All', nodes_string, max_concurrent=max_concurrent,
                                  env_file=env_file, dry_run=dry_run, debug=dry_run)

    i_log_file = log_file
    for i, cmd in enumerate(open(cmd_list).readlines()):
        if log_file is not None:
            i_log_file = log_file + f'.{i + 1}'
        pool.add(cmd.strip(), output_file=i_log_file)

    pool.execute()


@main.command('run_on_nodes')
@click.argument('cmd', nargs=-1)
@click.option('--nodes_string', '-n', help='Range of nodes to use', type=str, default='localhost')
@click.option('--env_file', '-e', help='Environment source file', type=t_file)
@click.option('--dry_run', '-d', help='Dry run, only print commands', is_flag=True)
def run_on_all_nodes(cmd, nodes_string, env_file, dry_run):
    ''' Run CMD on all nodes specified in argument.'''
    pool = worker.get_worker_pool('Run All', nodes_string, max_concurrent=2,
                                  env_file=env_file, dry_run=dry_run, debug=dry_run)

    cmd = ' '.join(cmd)

    for host in worker.get_hosts(nodes_string):
        pool.add(cmd, run_on_host=host)

    pool.execute()


@main.command('add_job')
@click.argument('name', type=str)
@click.argument('cmd', type=str)
@click.option('--target_node', '-t', help='Target node to use', type=str, default=None)
@click.option('--log_file', '-l', help='Log output to log_file', type=str, default=None)
def init_job(name, cmd, target_node, log_file):
    ''' Add a job to a job list file NAME. If job file does not exist, create one. '''
    if os.path.exists(name):        
        with open(name) as json_file:
            jobs = json.load(json_file)
    else:
        jobs = {'jobs': []}

    jobs['jobs'].append({'cmd': cmd.strip(), 'target_node': target_node, 'log_file': log_file})

    with open(name, 'w') as json_file:
        json.dump(jobs, json_file, indent=4)


@main.command('run_joblist')
@click.argument('name', type=t_file)
@click.option('--nodes_string', '-n', help='Range of nodes to use', type=str, default='localhost')
@click.option('--max_concurrent', '-m', help='Maximum concurrent tasks on a node', type=int, default=5)
@click.option('--env_file', '-e', help='Environment source file', type=t_file)
@click.option('--dry_run', '-d', help='Dry run, only print commands', is_flag=True)
@click.option('--worker_name', '-w', help='Name of the worker', type=str, default='Run joblist')
def run_joblist(name, nodes_string, max_concurrent, env_file, dry_run, worker_name):
    ''' Run all command listed in the job list file NAME.'''
    with open(name) as json_file:
        jobs = json.load(json_file)

    pool = worker.get_worker_pool(worker_name, nodes_string, max_concurrent=max_concurrent,
                                  env_file=env_file, dry_run=dry_run, debug=dry_run)

    for job in jobs['jobs']:
        pool.add(job['cmd'], output_file=job['log_file'], run_on_host=job['target_node'])

    pool.execute()


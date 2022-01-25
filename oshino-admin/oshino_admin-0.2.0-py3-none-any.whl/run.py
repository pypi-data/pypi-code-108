import sys
import subprocess

import pip
import requests
import yaml
import click

from oshino_admin import daemon
from oshino_admin.util import parse_plugin

@click.group()
def main():
    pass


@main.command('query')
@click.argument('q')
@click.option('--config', help='Config path', default='config.yaml')
def query(q, config):
    from oshino.config import Config, load
    from riemann_client.client import Client
    cfg = load(config)
    riemann = cfg.riemann
    transport_cls = cfg.riemann.transport
    transport = transport_cls(riemann.host, riemann.port)
    print("Executing query: {0}".format(q))
    with Client(transport) as client:
        print(client.query(q))


@main.group('config')
def config():
    pass


@config.command('init')
@click.argument('path')
def init_config(path):
    default_config = {
        'interval': 10,
        'riemann': {
            'host': 'localhost',
            'port': 5555
        },
        'agents': [
            {
                'name': 'health-check',
                'module': 'oshino.agents.http_agent.HttpAgent',
                'url': 'http://python.org',
                'tag': 'healthcheck'
            }
        ]
    }
    with open(path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)


@main.group('plugin')
def plugin():
    pass


def get_plugins():
    resp = requests.get('https://raw.githubusercontent.com/CodersOfTheNight/'
                        'oshino-admin/master/package_manager/plugins.txt')
    lines = resp.text.split('\n')
    return [parse_plugin(plugin) for plugin in lines
            if len(plugin.rstrip()) > 0]


def validate_plugin(fn):
    def wrapper(*args, **kwargs):
        plugins = get_plugins()
        package = kwargs['package_name']
        if not package in map(lambda x: x[0], plugins):
            print("Invalid plugin '{0}'".format(package))
            sys.exit(1)

        return fn(*args, **kwargs)

    return wrapper


@plugin.command('list')
def plugin_list():
    for package, desc in get_plugins():
        if package in sys.modules.keys():
            print('{0}* - {1}'.format(package, desc))
        else:
            print('{0} - {1}'.format(package, desc))


@plugin.command('install')
@click.argument('package_name')
@validate_plugin
def install(package_name):
    subprocess.call(['pip', 'install', package_name, '--upgrade'])


@plugin.command('uninstall')
@click.argument('package_name')
@validate_plugin
def uninstall(package_name):
    subprocess.call(['pip', 'uninstall', package_name])


@main.command('status')
@click.option('--pid', help='Pid for process', default='/var/run/oshino.pid')
def status(pid):
    daemon.status(pid)


@main.command('start')
@click.option('--config', help='Config path', default='config.yaml')
@click.option('--pid', help='Pid for process', default='/var/run/oshino.pid')
@click.option('--verbose/--normal', help='Verbose', default=False)
@click.option('--logfile', help='Where to put logs', default=None)
def start(config, pid, verbose, logfile):
    print('Starting...')
    daemon.start_daemon(config, pid, verbose, logfile)


@main.command('stop')
@click.option('--pid', help='Pid for process', default='/var/run/oshino.pid')
def stop(pid):
    print('Stopping...')
    daemon.stop_daemon(pid)



if __name__ == "__main__":
    main()

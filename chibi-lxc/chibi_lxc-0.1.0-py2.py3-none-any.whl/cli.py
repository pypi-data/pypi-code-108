# -*- coding: utf-8 -*-
import argparse
import datetime
import sys
import time

from chibi.config import basic_config, load as load_config
from chibi.file import Chibi_path
from chibi.snippet.list import group_by
from python_hosts import Hosts, HostsEntry

from chibi_lxc.config import configuration
from chibi_lxc.container import Not_exists_error


def get_ip( container, timeout=60 ):
    start = datetime.datetime.now()
    while ( datetime.datetime.now() - start ).total_seconds() < timeout:
        time.sleep( 3 )
        info = container.info
        if 'ip' in info:
            return info.ip
    raise TimeoutError( f"waiting {container.name}" )


def read_hosts():
    hosts_file = configuration.chibi_lxc.hosts
    hosts = Hosts( hosts_file )
    return hosts


def remove_host_if_exists( host ):
    hosts = read_hosts()
    entries = []
    for entry in hosts.entries:
        if host in entry.names:
            continue
        entries.append( entry )
    hosts.entries = entries
    hosts.write()


def init_hosts_file():
    hosts = read_hosts()
    hosts.entries = []
    hosts.add( [
        HostsEntry(
            entry_type='ipv4', address='127.0.0.1',
            names=[ 'localhost' ] ),
        HostsEntry(
            entry_type='ipv6', address='::1',
            names=[ 'localhost' ] ),
    ] )
    hosts.write()


def add_address_to_host( address, *hosts ):
    for host in hosts:
        remove_host_if_exists( host )
    hosts_in_file = read_hosts()
    if not hosts_in_file.entries:
        init_hosts_file()
        hosts_in_file = read_hosts()
    hosts_in_file.add( [ HostsEntry(
        entry_type='ipv4', address=address, names=list( hosts ) ) ] )
    hosts_in_file.write()


def main():
    parser = argparse.ArgumentParser(
        "tool for build containers" )
    parser.add_argument(
        "--log_level", dest="log_level", default="INFO",
        help="nivel de log", )

    parser.add_argument(
        "--config", type=Chibi_path, default=Chibi_path( 'config.py' ),
        help="python, yaml o json archivo con los settings" )

    sub_parsers = parser.add_subparsers(
        dest='command', help='sub-command help' )

    parser_list = sub_parsers.add_parser(
        'list', help='list the backups', )

    parser_start = sub_parsers.add_parser(
        'up', help='start the container', )
    parser_start.add_argument(
        "containers", nargs='+', metavar="containers",
        help="contenedores que se iniciaran" )

    parser_provision = sub_parsers.add_parser(
        'provision', help='start the container', )
    parser_provision.add_argument(
        "--only_files", dest='only_files', action="store_true",
        help="provisiona solo los archivos", )
    parser_provision.add_argument(
        "containers", nargs='+', metavar="containers",
        help="contenedores que se iniciaran" )

    parser_status = sub_parsers.add_parser(
        'status', help='', )
    parser_status.add_argument(
        "--scripts", "-s", dest='scripts', action="store_true",
        help="ejecuta los scripts de status", )
    parser_status.add_argument(
        "containers", nargs='*', metavar="containers",
        default=configuration.chibi_lxc.containers,
        help="contenedores que se iniciaran" )

    parser_info = sub_parsers.add_parser(
        'info', help='', )
    parser_info.add_argument(
        "containers", nargs='+', metavar="containers",
        help="contenedores que se iniciaran" )

    parser_destroy = sub_parsers.add_parser(
        'destroy', help='destroy the container', )
    parser_destroy.add_argument(
        "containers", nargs='+', metavar="containers",
        help="contenedores que se iniciaran" )

    parser_destroy.add_argument(
        "--force", "-f", action="store_true",
        help="fuerza a deneter el contenedor y lo destruye" )

    parser_stop = sub_parsers.add_parser(
        'stop', help='stop the container', )
    parser_stop.add_argument(
        "containers", nargs='+', metavar="containers",
        help="contenedores que se iniciaran" )

    parser_attach = sub_parsers.add_parser(
        'attach', help='attach the container', )
    parser_attach.add_argument(
        "container",
        help="contenedores que se hara attach" )

    parser_host = sub_parsers.add_parser(
        'host', help='update the host file', )
    parser_host.add_argument(
        "--update", "-u", action="store_true",
        help="actualiza el archivo de hosts en /etc/hosts" )

    args = parser.parse_args()
    basic_config( level=args.log_level )
    load_config( args.config )

    if args.command == 'list':
        containers = configuration.chibi_lxc.containers
        padding = max( map( lambda k: len( k ), containers.keys() ) )
        padding += 2
        padding_ip = len( '255.255.255.255' ) + 2
        space_ip = " " * padding_ip
        group_container = group_by(
            containers.values(), lambda c: c.__module__ )
        for group, list_of_container in group_container.items():
            print( group )
            for container in list_of_container:
                try:
                    if container.is_running:
                        ip = container.info.ip
                        print(
                            f"\t{container.name:{padding}} "
                            f"{ip:{padding_ip}} {container}" )
                    else:
                        print(
                            f"\t{container.name:{padding}} "
                            f"{space_ip} {container}" )
                except Not_exists_error:
                    print( f"\t{container.name:{padding}} {space_ip} {container}" )

    if args.command == 'up':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            container = containers[ container ]
            exists = container.exists
            if not exists:
                container.create()
            container.provision()
            container.start()
            ip = get_ip( container )
            add_address_to_host( ip, *container.hosts )
            if not exists:
                container.provision()
                container.run_scripts()

    if args.command == 'provision':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            if args.only_files:
                container = containers[ container ]
                container.provision()
            else:
                container = containers[ container ]
                container.provision()
                container.start()
                time.sleep( 10 )
                add_address_to_host( container.info.ip, *container.hosts )
                container.provision()
                container.run_scripts()

    if args.command == 'status':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            print( container )
            container = containers[ container ]
            if args.scripts:
                print()
                container.run_status_scripts()
            else:
                try:
                    info = container.info
                except Not_exists_error:
                    print( '\t', 'no exists' )
                    continue
                for k, v in info.items():
                    print( '\t', k, v )

    if args.command == 'host':
        if args.update:
            for container in configuration.chibi_lxc.containers.values():
                try:
                    add_address_to_host( container.info.ip, *container.hosts )
                except Not_exists_error:
                    pass
        else:
            print( '{:<15}{:<15}{:<15}{:}'.format(
                'name', 'state', 'ip', 'hosts' ) )
            for container in configuration.chibi_lxc.containers.values():
                try:
                    info = container.info
                    ip = info.ip
                    state = info.state
                    hosts = " ".join( container.hosts )
                    print( f'{container.name:<15}{state:<15}{ip:<15}{hosts}' )
                except Not_exists_error:
                    ip = '-'
                    state = 'not exists'
                    hosts = " ".join( container.hosts )
                    print( f'{container.name:<15}{state:<15}{ip:<15}{hosts}' )


    if args.command == 'info':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            print( container )
            container = containers[ container ]
            for s in container.scripts:
                print( '\t', s )

    if args.command == 'destroy':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            container = containers[ container ]
            if args.force and container.is_running:
                container.stop()
            container.destroy()

    if args.command == 'stop':
        containers = configuration.chibi_lxc.containers
        for container in args.containers:
            container = containers[ container ]
            container.stop()

    if args.command == 'attach':
        containers = configuration.chibi_lxc.containers
        container = containers[ args.container ]
        container.attach().run()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

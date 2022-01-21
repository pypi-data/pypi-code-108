import argparse
import sys
import os
from builtins import print


class PMPError(Exception):
    pass


# actions executing by commands
def version(args):
    from ._version import version
    print(version)


def find(args):
    from .find import _find
    _find(args.path)


def list(args):
    from .list import _list
    _list(args.long)


def acmd(args):
    from .acmd import _acmd
    _acmd(args.alias, args.body)


def dcmd(args):
    from .dcmd import _dcmd
    _dcmd(args.alias)


def lcmd(args):
    from .lcmd import _lcmd
    _lcmd()


def exec(args):
    from .exec import _exec
    _exec(args.alias, args.project)


def move(args):
    from .move import _move
    _move(args.project, args.destination)


# parser
def parser():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(help='commands')

    find_parser = s.add_parser('version', help='print version')
    find_parser.set_defaults(func=version)

    find_parser = s.add_parser('find', help='find projects in a directory')
    find_parser.add_argument('path', help='destination directory', default='.')
    find_parser.set_defaults(func=find)

    list_parser = s.add_parser('list', help='show list of available projects')
    list_parser.add_argument('--long', '-l', help='show full information', default=False, action='store_true')
    list_parser.set_defaults(func=list)

    acmd_parser = s.add_parser('acmd', help='add a command to open projects')
    acmd_parser.add_argument('alias', help='command alias')
    acmd_parser.add_argument('body', help='command body')
    acmd_parser.set_defaults(func=acmd)

    dcmd_parser = s.add_parser('dcmd', help='delete command to open projects')
    dcmd_parser.add_argument('alias', help='command alias')
    dcmd_parser.set_defaults(func=dcmd)

    dcmd_parser = s.add_parser('lcmd', help='list of commands to open projects')
    dcmd_parser.set_defaults(func=lcmd)

    exec_parser = s.add_parser('exec', help='open project')
    exec_parser.add_argument('alias', help='command alias')
    exec_parser.add_argument('project', help='project name or hash')
    exec_parser.set_defaults(func=exec)

    move_parser = s.add_parser('move', help='move project to other type catalog')
    move_parser.add_argument('project', help='project name (hash) to moving')
    move_parser.add_argument('destination', help='destination')
    move_parser.set_defaults(func=move)

    return p


# entry point
def main():

    # ---- create cache catalog and files if they not exist
    from ._meta import cache_root, cache_commands, cache_projects, cache_types

    if not os.path.exists(cache_root):
        os.mkdir(cache_root)

    if not os.path.exists(cache_commands):
        with open(cache_commands, 'w', encoding='utf-8') as file:
            file.write('{}')

    if not os.path.exists(cache_projects):
        with open(cache_projects, 'w', encoding='utf-8') as file:
            file.write('{}')

    if not os.path.exists(cache_types):
        with open(cache_types, 'w', encoding='utf-8') as file:
            file.write('{}')

    # ---- executing command
    p = parser()
    args = p.parse_args()

    if not hasattr(args, 'func'):
        p.print_help()
    else:
        try:
            args.func(args)
            return 0
        except PMPError as e:
            print(e, file=sys.stderr)

    return 1

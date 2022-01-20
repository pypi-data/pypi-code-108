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
    from dcmd import _dcmd
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


def debug(args):
    from ._meta import cache_root, cache_commands, cache_projects

    print('root:    ', cache_root, os.path.exists(cache_root))
    print('projects:', cache_projects, os.path.exists(cache_root))
    print('commands:', cache_commands, os.path.exists(cache_root))


# parser
def parser():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(help='commands')

    find_parser = s.add_parser('version', help='print version')
    find_parser.set_defaults(func=version)

    find_parser = s.add_parser('find', help='find projects in a directory')
    find_parser.add_argument('--path', '-p', help='destination directory', default='.')
    find_parser.set_defaults(func=find)

    list_parser = s.add_parser('list', help='show list of available projects')
    list_parser.add_argument('--long', '-l', help='show full information', default=False, action='store_true')
    list_parser.set_defaults(func=list)

    acmd_parser = s.add_parser('acmd', help='add a command to open projects')
    acmd_parser.add_argument('--alias', '-a', help='command alias', required=True)
    acmd_parser.add_argument('--body', '-b', help='command body', required=True)
    acmd_parser.set_defaults(func=acmd)

    dcmd_parser = s.add_parser('dcmd', help='delete command to open projects')
    dcmd_parser.add_argument('--alias', '-a', help='command alias', required=True)
    dcmd_parser.set_defaults(func=dcmd)

    find_parser = s.add_parser('find', help='find projects in a directory')
    find_parser.add_argument('--path', '-p', help='destination directory', default='.')
    find_parser.set_defaults(func=find)

    exec_parser = s.add_parser('exec', help='open project')
    exec_parser.add_argument('--alias', '-a', help='command alias', required=True)
    exec_parser.add_argument('--project', '-p', help='project name or hash', required=True)
    exec_parser.set_defaults(func=exec)

    move_parser = s.add_parser('move', help='move project to other type catalog')
    move_parser.add_argument('--project', '-p', help='project name (hash) to moving', required=True)
    move_parser.add_argument('--destination', '-d', help='destination', required=True)
    move_parser.set_defaults(func=move)

    move_parser = s.add_parser('debug', help='for developer')
    move_parser.set_defaults(func=debug)

    return p


# entry point
def main():

    # ---- create cache catalog and files if they not exist
    from ._meta import cache_root, cache_commands, cache_projects

    if not os.path.exists(cache_root):
        os.mkdir(cache_root)

    if not os.path.exists(cache_commands):
        with open(cache_commands, 'w', encoding='utf-8') as file:
            file.write('{}')

    if not os.path.exists(cache_projects):
        with open(cache_projects, 'w', encoding='utf-8') as file:
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

#!/usr/bin/env python3
# coding: utf-8

import volkanic.cmdline
from volkanic.utils import (
    desktop_open, where, where_site_packages
)


def run_where(_, args):
    if not args:
        return print(where_site_packages() or '')
    for arg in args:
        try:
            path = where(arg)
            print(arg, path, sep='\t')
        except ModuleNotFoundError:
            print(arg, 'ModuleNotFoundError', sep='\t')


def run_argv_debug(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


def run_desktop_open(_, args):
    args = args or ('.',)
    desktop_open(*args)


registry = volkanic.cmdline.CommandRegistry.from_entries({
    'volkanic.__main__:run_where': 'where',
    'volkanic.__main__:run_argv_debug': 'a',
    'volkanic.__main__:run_desktop_open': 'o',
})

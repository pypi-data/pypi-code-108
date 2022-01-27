#!/usr/bin/env python3
# coding: utf-8

import contextlib
import os
import sys
from collections import OrderedDict
from typing import Union

from volkanic.utils import load_symbol


@contextlib.contextmanager
def remember_cwd(path=None):
    """Temporarily change Current Working Directory (CWD/PWD)"""
    prev_cwd = os.getcwd()
    if path:
        os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def _flatten_recursively(tup: Union[tuple, list]) -> list:
    """
    >>> _flatten_recursively((1, (2, (3, 4))))
    [1, 2, 3, 4]
    """
    stack = list(tup)
    values = []
    while stack:
        val = stack.pop()
        if isinstance(val, (tuple, list)):
            stack.extend(val)
        else:
            values.append(val)
    values.reverse()
    return values


# experimental
class CommandOptionDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(CommandOptionDict, self).__init__(*args, **kwargs)
        self.pargs = []
        self.executable = 'echo'

    @classmethod
    def _tuple_expand(cls, source_pairs, target_pairs: list):
        """expand nested tuples -- recursively -- deprecated"""
        for key, val in source_pairs:
            if not isinstance(val, tuple):
                target_pairs.append((key, val))
                continue
            # when val is of type tuple
            pairs = [(key, v) for v in val]
            cls._tuple_expand(pairs, target_pairs)

    @classmethod
    def _expand(cls, key, val):
        if isinstance(val, tuple):
            for val in _flatten_recursively(val):
                yield key, val
        else:
            yield key, val

    @classmethod
    def _explode(cls, key, val):
        if val is None or val is False:
            return []
        if val is True:
            return [key]
        if isinstance(val, (list, tuple)):
            return [key] + list(val)
        return [key, str(val)]

    def as_args(self):
        parts = [self.executable]
        for pair in self.items():
            for key, val in self._expand(*pair):
                parts.extend(self._explode(key, val))
        parts.extend(self.pargs)
        return parts

    def __str__(self):
        import shlex
        args = [shlex.quote(s) for s in self.as_args()]
        return ' '.join(args)

    def run(self, dry=False, quiet=False, **kwargs):
        if not quiet:
            print(self, file=sys.stderr)
        if not dry:
            import subprocess
            return subprocess.run(self.as_args(), **kwargs)

    def __call__(self, executable, *pargs):
        # for convenience
        self.executable = executable
        self.pargs = list(pargs)
        return self


class CommandRegistry(object):
    def __init__(self, commands, prog=''):
        self.commands = commands
        self.default_prog = prog

    @classmethod
    def from_cmddef(cls, cmddef, prog=''):
        commands = {}
        for line in cmddef.splitlines():
            line = line.strip()
            if not line:
                continue
            cmd, dotpath = line.split()[:2]
            commands[cmd] = dotpath
        return cls(commands, prog)

    @classmethod
    def from_entries(cls, entries, prog=''):
        return cls({v: k for k, v in entries.items()}, prog)

    def show_commands(self, prog):
        indent = ' ' * 4
        lines = ['available commands:', '']
        for cmd in sorted(self.commands):
            lines.append(indent + ' '.join([prog, cmd]))
        print(*lines, sep='\n', end='\n\n')

    def get_real_prog(self, argv):
        if not argv:
            return self.default_prog or '<prog>'
        if argv[0].endswith('.py'):
            return self.default_prog or argv[0]
        return os.path.basename(argv[0])

    def __call__(self, argv=None):
        argv = sys.argv if argv is None else list(argv)
        real_prog = self.get_real_prog(argv)
        try:
            dotpath = self.commands[argv[1]]
        except LookupError:
            self.show_commands(real_prog)
            sys.exit(1)

        # intended use: argparse.ArgumentParser(prog=prog)
        prog = '{} {}'.format(real_prog, argv[1])

        if ':' not in dotpath:
            dotpath += ':run'
        return load_symbol(dotpath)(prog, argv[2:])

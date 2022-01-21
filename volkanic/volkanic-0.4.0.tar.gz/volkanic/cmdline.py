#!/usr/bin/env python3
# coding: utf-8

import contextlib
import os
import sys
from collections import OrderedDict

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


# experimental
class CommandOptionDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(CommandOptionDict, self).__init__(*args, **kwargs)
        self.pargs = []
        self.executable = 'echo'

    @classmethod
    def _tuple_expand(cls, source_pairs, target_pairs: list):
        """expand nested tuples -- recursively"""
        for key, val in source_pairs:
            if not isinstance(val, tuple):
                target_pairs.append((key, val))
                continue
            # when val is of type tuple
            pairs = [(key, v) for v in val]
            cls._tuple_expand(pairs, target_pairs)

    def as_args(self):
        pairs = []
        parts = [self.executable]
        self._tuple_expand(self.items(), pairs)
        for key, val in pairs:
            if val is None or val is False:
                continue
            parts.append(key)
            if val is True:
                pass
            elif isinstance(val, list):
                parts.extend(val)
            else:
                parts.append(str(val))
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

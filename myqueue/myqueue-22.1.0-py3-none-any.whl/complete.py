#!/usr/bin/env python3
"""Bash completion.

Put this in your .bashrc::

    complete -o default -C "python3 -m myqueue.complete" mq

"""

from __future__ import annotations
import os
import sys
from typing import Any, Iterable, Mapping


def read() -> dict[str, Any]:
    """Read queue as a dict."""
    from pathlib import Path
    import json
    from myqueue.config import find_home_folder
    home = find_home_folder(Path('.').resolve())
    path = home / '.myqueue/queue.json'
    try:
        dct: dict[str, Any] = json.loads(path.read_text())
        return dct
    except Exception:
        return {}


# Beginning of computer generated data:
commands = {
    'completion':
        ['-v', '--verbose', '-q', '--quiet', '-T', '--traceback'],
    'config':
        ['-Q', '--queue-name', '--in-place', '-z', '--dry-run', '-v',
         '--verbose', '-q', '--quiet', '-T', '--traceback'],
    'daemon':
        ['-z', '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback'],
    'help':
        [''],
    'info':
        ['-v', '--verbose', '-q', '--quiet', '-T', '--traceback', '-i',
         '--id', '-A', '--all'],
    'init':
        ['-z', '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback'],
    'kick':
        ['-z', '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback'],
    'list':
        ['-s', '--states', '-i', '--id', '-n', '--name', '-e', '--error',
         '-c', '--columns', '-S', '--sort', '-C', '--count',
         '-L', '--use-log-file', '--not-recursive', '-v',
         '--verbose', '-q', '--quiet', '-T', '--traceback'],
    'modify':
        ['-E', '--email', '-N', '--new-state', '-s', '--states', '-i',
         '--id', '-n', '--name', '-e', '--error', '-z',
         '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback', '-r', '--recursive'],
    'remove':
        ['-s', '--states', '-i', '--id', '-n', '--name', '-e', '--error',
         '-z', '--dry-run', '-v', '--verbose', '-q', '--quiet',
         '-T', '--traceback', '-r', '--recursive'],
    'resubmit':
        ['-R', '--resources', '-w', '--workflow', '-s', '--states', '-i',
         '--id', '-n', '--name', '-e', '--error', '-z',
         '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback', '-r', '--recursive'],
    'run':
        ['-n', '--name', '-w', '--workflow', '-z', '--dry-run', '-v',
         '--verbose', '-q', '--quiet', '-T', '--traceback'],
    'submit':
        ['-d', '--dependencies', '-n', '--name', '--restart', '-f',
         '--force', '--max-tasks', '-R', '--resources', '-w',
         '--workflow', '-z', '--dry-run', '-v', '--verbose',
         '-q', '--quiet', '-T', '--traceback'],
    'sync':
        ['-z', '--dry-run', '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback'],
    'workflow':
        ['-f', '--force', '--max-tasks', '-t', '--targets', '-p',
         '--pattern', '-a', '--arguments', '-z', '--dry-run',
         '-v', '--verbose', '-q', '--quiet', '-T',
         '--traceback']}
# End of computer generated data

aliases = {'rm': 'remove',
           'ls': 'list'}


def complete(word: str, previous: str, line: str, point: int) -> Iterable[str]:
    for w in line[:point - len(word)].strip().split()[1:]:
        if w[0].isalpha():
            if w in commands or w in aliases:
                command = aliases.get(w, w)
                break
    else:
        opts = ['-h', '--help', '-V', '--version']
        if word[:1] == '-':
            return opts
        return list(commands) + list(aliases) + opts

    if word[:1] == '-':
        return commands[command]

    if previous in ['-n', '--name']:
        dct = read()
        words = set()
        for task in dct['tasks']:
            cmd = task['cmd']
            words.add((cmd['cmd'] + '+' + '_'.join(cmd['args'])).rstrip('+'))
        return words

    if previous in ['-i', '--id']:
        dct = read()
        return {str(task['id']) for task in dct['tasks']}

    if command == 'help':
        return [cmd for cmd in (list(commands) + list(aliases))
                if cmd != 'help']

    if command == 'daemon':
        return ['start', 'stop', 'status']

    return []


def main(environ: Mapping[str, str], word: str, previous: str) -> None:
    line = environ['COMP_LINE']
    point = int(environ['COMP_POINT'])
    words = complete(word, previous, line, point)
    for w in words:
        if w.startswith(word):
            print(w)


if __name__ == '__main__':
    main(os.environ, *sys.argv[2:])  # pragma: no cover

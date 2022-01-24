from __future__ import annotations
import os
import sys
from collections import defaultdict
from pathlib import Path

from myqueue.task import Task
from myqueue.utils import mqhome


def colored(state: str) -> str:
    """Yellow for running, red for bad, green for done."""
    if state.isupper():
        return '\033[91m' + state + '\033[0m'
    if state.startswith('done'):
        return '\033[92m' + state + '\033[0m'
    if state.startswith('running'):
        return '\033[93m' + state + '\033[0m'
    return state


def pprint(tasks: list[Task],
           verbosity: int = 1,
           columns: str = 'ifnaIrAste',
           short: bool = False,
           maxlines: int = 9999999999) -> None:
    """Pretty-print tasks.

    Use short=True to get only a summary.
    """
    if verbosity < 0:
        return

    if not tasks:
        return

    home = str(mqhome()) + '/'
    cwd = str(Path.cwd()) + '/'

    if columns.endswith('-'):
        columns = ''.join(c for c in 'ifnaIrAste' if c not in columns[:-1])

    titles = ['id', 'folder', 'name', 'args', 'info',
              'res.', 'age', 'state', 'time', 'error']
    c2i = {c: i for i, c in enumerate('ifnaIrAste')}
    indices = [c2i[c] for c in columns]

    if len(tasks) > maxlines:
        cut1 = maxlines // 2
        cut2 = maxlines - cut1 - 2
        skipped = len(tasks) - cut1 - cut2
        tasks = tasks[:cut1] + tasks[-cut2:]
    else:
        skipped = 0

    lines = []
    lengths = [0] * len(columns)

    count: dict[str, int] = defaultdict(int)
    for task in tasks:
        words = task.words()
        _, folder, _, _, _, _, _, state, _, _ = words
        count[state] += 1
        if folder.startswith(cwd):
            words[1] = './' + folder[len(cwd):]
        elif folder.startswith(home):
            words[1] = '~/' + folder[len(home):]
        words = [words[i] for i in indices]
        lines.append(words)
        lengths = [max(n, len(word)) for n, word in zip(lengths, words)]

    # remove empty columns ...
    lines = [[word for word, length in zip(words, lengths) if length]
             for words in lines]
    columns = ''.join(c for c, length in zip(columns, lengths) if length)
    lengths = [length for length in lengths if length]

    if skipped:
        lines[cut1:cut1] = [[f'... ({skipped} tasks not shown)']]

    if verbosity:
        lines[:0] = [[titles[c2i[c]] for c in columns]]
        lengths = [max(length, len(title))
                   for length, title in zip(lengths, lines[0])]

    try:
        N = os.get_terminal_size().columns
        cut = max(0, N - sum(L + 1 for L, c in zip(lengths, columns)
                             if c != 'e'))
    except OSError:
        cut = 999999

    if verbosity:
        lines[1:1] = [['-' * L for L in lengths]]
        lines.append(lines[1])

    use_color = sys.stdout.isatty() and 'MYQUEUE_TESTING' not in os.environ

    if not short:
        for words in lines:
            words2 = []
            for word, c, L in zip(words, columns, lengths):
                if c == 'e':
                    word = word[:cut]
                elif c in 'At':
                    word = word.rjust(L)
                else:
                    word = word.ljust(L)
                    if c == 's' and use_color:
                        word = colored(word)
                words2.append(word)
            print(' '.join(words2))

    if verbosity:
        count['total'] = len(tasks)
        print(', '.join(f'{colored(state) if use_color else state}: {n}'
                        for state, n in count.items()))

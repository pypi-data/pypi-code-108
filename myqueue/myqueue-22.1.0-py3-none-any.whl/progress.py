"""Progress-bar."""
from __future__ import annotations
import os
import sys
from typing import Iterator


def progress_bar(length: int,
                 message: str = '',
                 verbosity: int = 1) -> Iterator[int]:
    """Progress-bar.

    Example::

        pb = progress_bar(10, 'Text:')
        for i in range(10):
            ...
            next(pb)

    Output::

        Text: |--------------------| 100.0%
    """
    if verbosity == 0:
        return iter(range(length))

    if sys.stdout.isatty():
        print(f'{message} |                    |   0.0%', end='', flush=True)
    else:
        print(f'{message} ', end='', flush=True)

    return _progress_bar(length, message)


def _progress_bar(length: int,
                  message: str = '') -> Iterator[int]:
    if not sys.stdout.isatty():
        for n in range(length):
            if n == length - 1:
                print('|--------------------| 100.0%')
            yield n
        return

    for n in range(length):
        p = 100 * (n + 1) / length
        bar = '-' * int(round(20 * (n + 1) / length))
        print(f'\r{message} |{bar:20}| {p:5.1f}%',
              end='',
              flush=True)
        if n == length - 1:
            print()
        yield n


class Spinner:
    def __init__(self) -> None:
        """Print the characters .oOo.oOo.oOo.oOo and so on."""
        if sys.stdout.isatty():
            self.fd = sys.stdout
        else:
            self.fd = open(os.devnull, 'w')
        self.n = 0

    def spin(self) -> None:
        """Spin the spinner."""
        N = 500
        if self.n % N == 0:
            self.fd.write('\r' + '.oOo'[(self.n // N) % 4])
            self.fd.flush()
        self.n += 1

    def reset(self) -> None:
        """Place cursor at the beginning of the line."""
        self.n = 0
        self.fd.write('\r')


def main(x: float = 1) -> None:
    """Demo."""
    from time import sleep
    pb = progress_bar(500, 'Test 1:')
    for _ in range(500):
        sleep(0.002 * x)
        next(pb)
    pb = progress_bar(500, 'Test 2:', 0)
    for _ in range(500):
        next(pb)
    pb = progress_bar(5, 'Test 3:')
    for _ in range(5):
        sleep(0.5 * x)
        next(pb)
    spinner = Spinner()
    for _ in range(10000):
        spinner.spin()
        sleep(0.00005 * x)
    spinner.reset()
    print('Done!')


if __name__ == '__main__':
    main()

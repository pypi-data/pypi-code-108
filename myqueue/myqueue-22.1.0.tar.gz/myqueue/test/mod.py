"""Module for testing a module as a task."""
from __future__ import annotations
import sys


def main():
    """Print CLI-args."""
    for arg in sys.argv:
        print(arg)


if __name__ == '__main__':
    main()

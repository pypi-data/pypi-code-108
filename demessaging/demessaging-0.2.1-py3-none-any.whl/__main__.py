import sys

from demessaging import main
from demessaging.cli import UNKNOWN_MODULE


def _main():
    sys.path.insert(0, ".")
    return main(UNKNOWN_MODULE)


if __name__ == "__main__":
    _main()

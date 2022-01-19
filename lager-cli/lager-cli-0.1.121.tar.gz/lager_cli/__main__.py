"""
    __main__

    Main entry point when running as a module
"""
import sys

from .cli import cli


if __name__ == "__main__":
    sys.exit(cli())

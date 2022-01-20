import os

from polidoro_cli.cli.cli import CLI

CLI_DIR = os.environ.get('CLI_DIR', os.path.expanduser('~/.cli'))

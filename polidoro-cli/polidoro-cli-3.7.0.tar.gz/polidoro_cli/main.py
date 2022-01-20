import os
import sys

from subprocess import CalledProcessError
from polidoro_argument import PolidoroArgumentParser

from polidoro_cli.cli import CLI_DIR

from polidoro_cli.cli.cli import CLI


def load_clis(cli_dir):
    sys.path.insert(0, cli_dir)
    clis_py = []
    clis_cli = []
    for file in os.listdir(cli_dir):
        full_path = os.path.join(cli_dir, file)
        if os.path.isfile(full_path) and not file.startswith('__'):
            if file.endswith('.py'):
                clis_py.append(file.replace('.py', ''))
            elif file.endswith('.cli'):
                clis_cli.append(full_path)

    # Load all <CLI>.py
    for py in clis_py:
        __import__(py)

    # Load all <CLI>.cli
    for cli in clis_cli:
        CLI.create_file_commands(cli)


def main():
    # Load CLIs
    load_clis(CLI_DIR)

    try:
        from polidoro_cli import VERSION
        PolidoroArgumentParser(version=VERSION, prog='cli').parse_args()
    except CalledProcessError as error:
        return error.returncode
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    os.environ['CLI_PATH'] = os.path.dirname(os.path.realpath(__file__))

    main()

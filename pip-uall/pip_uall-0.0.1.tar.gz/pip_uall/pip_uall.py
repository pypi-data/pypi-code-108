from configparser import ConfigParser
from pathlib import Path
import subprocess
import logging
import tempfile


LOG_FILE = f'{tempfile.mktemp()}.log'
COLOR_RED = '\x1b[0;31m'
COLOR_GREEN = '\x1b[0;32m'
COLOR_RESET = '\x1b[0;0m'


logging.basicConfig(filename=Path(LOG_FILE), filemode='w')


def read_config() -> tuple[list[str], list[str]]:
    parser = ConfigParser()
    tmp = Path.joinpath(Path.home(), '.pipuall.ini')
    parser.read(tmp)
    return (
        parser['pip_uall']['pip_commands'].split(','),
        parser['pip_uall']['excluded'].split(',')
    )


def main() -> int:
    print(f'logs can be found in {LOG_FILE}\n')
    pip_commands, excluded = read_config()
    for pip_command in pip_commands:
        process = subprocess.run(
            [pip_command, 'freeze'],
            stdout=subprocess.PIPE
        )
        for package in process.stdout.decode('utf-8').split('\n')[:-1]:
            name, _ = package.split('==')
            if name not in excluded:
                print(f'{name}...', end='\t')
                upgrade_process = subprocess.run(
                    [pip_command, 'install', '--upgrade', name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                if upgrade_process.stderr != b'':
                    print(f'{COLOR_RED}failed{COLOR_RESET}')
                    logging.exception(upgrade_process.stderr.decode('utf-8'))
                else:
                    print(f'{COLOR_GREEN}success{COLOR_RESET}')
    return 0

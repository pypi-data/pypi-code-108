import subprocess
import logging
import datetime
import os
from pathlib import Path
from configparser import ConfigParser


LOG_DIR = Path(f'{Path.home()}/.pip_uall/')
LOG_FILE = Path(f'{LOG_DIR}{datetime.datetime.now().strftime("%m-%d-%y")}.log')
COLOR_RED = '\x1b[0;31m'
COLOR_GREEN = '\x1b[0;32m'
COLOR_RESET = '\x1b[0;0m'


LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, filemode='w')


def read_config() -> tuple[list[str], list[str]]:
    parser = ConfigParser()
    tmp = Path.joinpath(Path.home(), '.pipuall.ini')
    parser.read(tmp)
    return (
        parser['pip_uall']['pip_commands'].split(','),
        parser['pip_uall']['excluded'].split(',')
    )


def clean_logs():
    for log_file in LOG_DIR.iterdir():
        os.remove(log_file)


def install_package(name: str, pip_command: str) -> bytes:
    print(f'{name}...', end='\t')
    upgrade_process = subprocess.run(
        [pip_command, 'install', '--upgrade', name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )
    return upgrade_process.stderr


def install_packages(packages: bytes, pip_command: str, excluded_packages: list[str]) -> None:
    for package in packages.decode('utf-8').split('\n')[:-1]:
        try:
            name, _ = package.split('==')
        except ValueError:
            name, _ = package.split(" @ ")
        
        if name not in excluded_packages:
            stderr = install_package(name, pip_command)
        else:
            continue
        
        if stderr != b'':
            print(f'{COLOR_RED}failed{COLOR_RESET}')
            logging.exception(stderr.decode('utf-8'))
        else:
            print(f'{COLOR_GREEN}success{COLOR_RESET}')


def main() -> int:
    print(f'logs can be found in {LOG_FILE}\n')
    pip_commands, excluded = read_config()
    for pip_command in pip_commands:
        process = subprocess.run(
            [pip_command, 'freeze'],
            stdout=subprocess.PIPE
        )
        install_packages(process.stdout, pip_command, excluded)
    return 0

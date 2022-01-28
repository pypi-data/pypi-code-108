#!/usr/bin/env python3

import argparse
import logging
import sys
import traceback
from pathlib import Path

import packaging.version
import pkg_resources
import requests

from . import twitch

logger = logging.getLogger(__name__)


def run_argparse(bundled):
    def path_check_file_exists(value):
        try:
            path = Path(value)
        except:
            raise argparse.ArgumentTypeError(f'Could not parse path "{value}"')
        if not path.is_file():
            raise argparse.ArgumentTypeError(f'"{value}" does not exist or is not a file')
        return path

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@', exit_on_error=not bundled)
    parser.add_argument('--config', type=path_check_file_exists, default='config.txt', help='Configuration file')
    parser.add_argument('--quiet', action='store_true', help='Suppress startup sound')
    parser.add_argument('--debug', action='store_true', help='Extra logging')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + pkg_resources.get_distribution(__package__).version)

    return vars(parser.parse_args())


update_str = r'''
 _   _ ____  ____    _  _____ _____      ____  
| | | |  _ \|  _ \  / \|_   _| ____|   _|  _ \ 
| | | | |_) | | | |/ _ \ | | |  _|    (_) | | |
| |_| |  __/| |_| / ___ \| | | |___    _| |_| |
 \___/|_|   |____/_/   \_\_| |_____|  (_)____/ 
'''


def version_check():
    try:
        response = requests.get('https://api.github.com/repos/vilhelmen/djallin2/releases',
                                headers={'Accept': 'application/vnd.github.v3+json'})
        response.raise_for_status()
        response = [(packaging.version.parse(rel['tag_name']), rel) for rel in response.json()]
    except Exception as err:
        logging.error(f'Error running update check: {err}')
        return

    current_ver = packaging.version.parse(pkg_resources.get_distribution(__package__).version)

    if not current_ver.is_prerelease:
        # hide dev versions
        response = list(filter(lambda x: not x[0].is_prerelease, response))

    latest = response[0]

    if latest[0] > current_ver:
        logging.info(update_str)
        logging.info(latest[1]['html_url'])


def boot():
    # Just for reference for now
    bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

    try:
        args = run_argparse(bundled)

        logging.basicConfig(level=logging.DEBUG if args['debug'] else logging.INFO,
                            format='%(levelname)s:%(threadName)s:%(message)s')
        logger.setLevel(logging.DEBUG if args['debug'] else logging.INFO)

        version_check()

        twitch.launch_system(args['config'], args['quiet'], args['debug'])
    except Exception as err:
        if True or bundled:
            logging.critical(twitch.dead_msg)
            logging.critical(traceback.format_exc())
            input('Press enter to exit...')
        else:
            raise

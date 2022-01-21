import getopt
import imp
import os
import sys

import fire

import twidi.console.console
from twidi import logger


# TODO Arbitrary loading of code is no good
def load_from_file(filepath):
    global py_mod

    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    return py_mod


def start(config_path=None):
    from twidi.config import config
    from twidi.bots.bot import EyesyBot
    config_file = config
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not config_path:
        config_file_path= os.path.join(dir_path, '..', 'config.py')
    else:
        config_file_path = config_path
    try:
        loaded_config = load_from_file(config_file_path)
        config_file = loaded_config
    except Exception as e:
        logger.error(f'Invalid config file specified {str(e)}')
    sys.exit(EyesyBot(
        midi_commands=config_file.midi_commands, prefix=config_file.prefix, token=config_file.token,
        initial_channel=config_file.channel
    ).run())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config_path')
    parser.add_argument('-d', '--debug', const='debug', action='store_const',)
    args = parser.parse_args()
    if hasattr(args, 'debug') and args.debug:
        twidi.console.console.show_midi_device_information()
    else:
        if hasattr(args, 'config_path') and args.config_path:
            start(config_path=args.config_path)
        else:
            start()

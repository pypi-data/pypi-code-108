import sys
import fire

from twidi.config.loader import load_config
from twidi.console.console import ConsoleApp


def start(config_path=None):
    from twidi.bots.bot import EyesyBot

    config_file = load_config(config_path)
    sys.exit(
        EyesyBot(
            midi_commands=config_file.midi_commands,
            prefix=config_file.prefix,
            token=config_file.token,
            initial_channel=config_file.channel,
        ).run()
    )


def main():
    fire.Fire()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_path')
    parser.add_argument('-d', '--debug', const='debug', action='store_const', )
    args = parser.parse_args()
    if hasattr(args, 'debug') and args.debug:
        twidi.console.console.show_midi_device_information()
    else:
        if hasattr(args, 'config_path') and args.config_path:
            start(config_path=args.config_path)
        else:
            start()
    """
    return


if __name__ == "__main__":
    console_app = ConsoleApp()
    fire.Fire(console_app)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_path')
    parser.add_argument('-d', '--debug', const='debug', action='store_const', )
    args = parser.parse_args()
    if hasattr(args, 'debug') and args.debug:
        twidi.console.console.show_midi_device_information()
    else:
        if hasattr(args, 'config_path') and args.config_path:
            start(config_path=args.config_path)
        else:
            start()
    
    """

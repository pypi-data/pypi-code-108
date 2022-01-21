import logging

import fire

from twidi.bots.bot import EyesyBot
from twidi.commands.midi.midi_command import MidiCommand
from twidi.config.config import midi_commands
from twidi.debug import main as print_debug_info

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

'''
from twidi.console.console import show_midi_device_information
'''
def show_midi_device_information():
    print_debug_info()

def test_midi_command(command_name: str, value: int, device_id=None):
    if device_id:
        for command in midi_commands:
            command.device_id = device_id
    bot = EyesyBot(midi_commands=midi_commands, token='', initial_channel='', prefix='')
    # noinspection PyTypeChecker
    command: MidiCommand = bot.get_command(name=command_name)
    message = command.message.to_mido_message(value=value)
    command.send_midi_message(message)

if __name__ == '__main__':
    fire.Fire(show_midi_device_information)
    fire.Fire(test_midi_command)

"""
Example MIDI configuration which will be passed to your bot.
Will eventually add support to define configs on a use-case level
using Cogs from TwitchIO
"""
from enum import Enum

from twidi.commands.midi.midi_command import MidiCommandArgument, MidiControlCommand
from twidi.commands.midi.midi_message import ControlMessage


class Device(Enum):
    DEFAULT = 'MRCC'
    MRCC = 'MRCC'
    YOUR_DEVICE = 'YOUR_DEVICE_ID'


prefix = '!eyesy'
token='o68hi96er2zyx7iqaafxrmb1ucgw8i'
channel = 'grogoyle'
backend = ''
midi_commands = [
    MidiControlCommand(
        device_id=Device.DEFAULT.value,
        name='eyesy1',
        aliases=['knob1', '1'],
        message=ControlMessage(cc_number=7, channel=0, value=50, allow_custom_value=True),
        arguments=[
            MidiCommandArgument(
                name='value',
                min=0,
                max=127,
                validations=[lambda x: 0 <= x <= 127, lambda x: type(x) == int or str.isnumeric(x)],
            )
        ],
        cooldown_in_seconds=30,
        mod_only=False,
        help='Control Knob 1',
        description='Control Knob 1 Desc',
    ),
]

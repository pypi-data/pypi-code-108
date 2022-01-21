import pytest

from twidi.commands import MidiControlCommand, MidiCommandArgument
from twidi.commands import ControlMessage


def test_command_constructor():
    options = MidiControlCommand(
        device_id='device_1',
        name='eyesy1',
        aliases=['knob1', '1'],
        message=ControlMessage(cc_number=21, channel=12, value=50, allow_custom_value=True),
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
    )
    assert options is not None

@pytest.mark.skip
def test_command_to_dict():
    return

@pytest.mark.skip
def test_command_from_dict():
    return


@pytest.mark.skip()
def test_command_to_yaml():
    return
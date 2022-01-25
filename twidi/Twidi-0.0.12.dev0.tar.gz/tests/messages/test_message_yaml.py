import json

import yaml
import yamlable

from twidi.commands import ControlMessage
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def test_control_message_to_dict():
    control_message = ControlMessage(cc_number=1, channel=1, value=10)
    control_message_dict = control_message.to_dict()
    assert control_message is not None
    assert control_message_dict.get('message_type') == 'CONTROL_CHANGE'


def test_control_message_to_yaml():
    control_message = ControlMessage(cc_number=1, channel=1, value=10)
    control_message_yaml = control_message.to_dict()
    assert control_message_yaml is not None

def test_control_message_from_dict():
    control_message = ControlMessage(cc_number=1, channel=1, value=10)
    control_message_yaml = control_message.to_dict()
    loaded_dict = ControlMessage.from_dict(control_message_yaml)
    assert loaded_dict is not None

def test_control_message_to_json():
    control_message = ControlMessage(cc_number=1, channel=1, value=10)
    control_message_yaml = control_message.to_dict()
    json_message = json.dumps(control_message_yaml)
    assert json_message is not None

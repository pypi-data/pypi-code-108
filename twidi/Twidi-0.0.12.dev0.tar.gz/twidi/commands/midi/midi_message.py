from enum import Enum
from typing import Dict, Any

import mido
from yamlable import YamlAble, yaml_info

""" Message Argument Options
===========  ======================  ================
Name         Valid Range             Default Value
===========  ======================  ================
channel      0..15                   0
frame_type   0..7                    0
frame_value  0..15                   0
control      0..127                  0
note         0..127                  0
program      0..127                  0
song         0..127                  0
value        0..127                  0
velocity     0..127                  64
data         (0..127, 0..127, ...)   () (empty tuple)
pitch        -8192..8191             0
pos          0..16383                0
time         any integer or float    0
===========  ======================  ================
"""


class MessageType(Enum):
    """
    The available MIDI message types
    """

    NO_TYPE = "undefined"
    PITCH_WHEEL = "pitchwheel"
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CONTROL_CHANGE = "control_change"
    POLY_TOUCH = "polytouch"
    AFTER_TOUCH = "aftertouch"
    START = "start"
    RESET = "reset"
    STOP = "stop"
    CONTINUE = "continue"


@yaml_info(yaml_tag="MidiMessage")
class MidiMessage(YamlAble):
    default_value = None
    allow_custom_value = True
    last_called = -1
    _value: int = None
    message_type: MessageType = MessageType.NO_TYPE

    def __init__(
        self, value=0, channel=0, min=0, max=127, allow_custom_value=True, **kwargs
    ):
        self.min = min
        self.max = max
        self.value = value
        self.channel = channel
        self.allow_custom_value = allow_custom_value

    @staticmethod
    def validate(**kwargs):
        raise NotImplementedError()

    def to_mido_message(self, **kwargs) -> mido.Message:
        raise NotImplementedError()

    def to_dict(self):  # type: (...) -> Dict[str, Any]
        as_dict = super(MidiMessage, self).__to_yaml_dict__()
        as_dict.update({"message_type": self.message_type.name})
        value = as_dict.pop("_value")
        as_dict.update({"value": value})
        return as_dict

    @staticmethod
    def from_dict(class_dict):
        return MidiMessage(**class_dict)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not self.allow_custom_value:
            return
        else:
            self._value = value


class ControlMessage(MidiMessage):
    message_type: MessageType = MessageType.CONTROL_CHANGE

    def __init__(
        self,
        cc_number: int,
        value: int = 0,
        channel: int = 0,
        message_type=MessageType.CONTROL_CHANGE,
        **kwargs,
    ):
        super().__init__(value=value, channel=channel, **kwargs)
        self.channel = channel
        self.cc_number = cc_number

    def to_mido_message(self, value: int = None, **kwargs) -> mido.Message:
        """
        Create a message to send to MIDO - MIDO message values can be overridden see docs for
        list of available options
        :param cc_number: CC number - IE - 7
        :param value: Valid int, usually 0-127
        :param kwargs: Any valid MIDO options
        :return:
        """

        val = self.value
        if self.allow_custom_value and value:
            val = value
        elif value:
            raise ValueError("Command does not allow custom values")
        channel = kwargs.get("channel", self.channel)
        return mido.Message(
            "control_change", control=self.cc_number, value=val, channel=channel
        )

    @staticmethod
    def from_dict(class_dict):
        return ControlMessage(**class_dict)


class NoteMessage(MidiMessage):

    duration = 0

    def to_mido_message(self, value: int = None, **kwargs) -> mido.Message:
        """
        Create a message to send to MIDO - MIDO message values can be overridden see docs for
        list of available options
        :param cc_number: CC number - IE - 7
        :param value: Valid int, usually 0-127
        :param kwargs: Any valid MIDO options
        :return:
        """

        val = self.value
        if self.allow_custom_value and value:
            val = value
        elif value:
            raise ValueError("Command does not allow custom values")

        # TODO Simply pass along kwargs to mido
        channel = kwargs.get("channel", self.channel)
        note_off = kwargs.get("note_off", False)
        if not note_off:
            return mido.Message("note_on", value=val, channel=channel)
        else:
            return mido.Message("note_off", value=val, channel=channel)

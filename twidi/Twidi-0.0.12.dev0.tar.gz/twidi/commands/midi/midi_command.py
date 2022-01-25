import datetime
import threading
from dataclasses import dataclass
from enum import Enum
from typing import List, Callable, Dict, Any

import mido
from twitchio.ext import commands

from twidi.logger import logger
from twidi.commands.midi.midi_message import MessageType, MidiMessage
from yamlable import yaml_info, YamlAble


@dataclass
class MidiCommandArgument:
    validations: List[Callable] = None
    name: str = "value"
    min: int = 0
    max: int = 127


class MidiCommandType(Enum):
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


@yaml_info(yaml_tag="MidiCommand")
class MidiCommand(commands.Command, YamlAble):
    """Base class for all MIDI commands"""

    device_id: str
    command_type: MidiCommandType
    last_called: datetime.datetime = None
    arguments: List[MidiCommandArgument]
    cooldown_in_seconds: int
    value: int
    mod_only: bool
    out_port = None
    help_text: str = "Help not defined"
    description: str = "Description not defined"
    help_trigger = "help"
    description_trigger = "description"

    def __init__(
        self,
        name: str,
        device_id: str,
        message: MidiMessage,
        arguments: List[MidiCommandArgument],
        func: Callable = None,
        mod_only=False,
        help=None,
        cooldown_in_seconds=None,
        backend = "mido.backends.pygame",
        description=None,
        **attrs,
    ):
        super().__init__(name, func or self.handle_command, **attrs)
        self.help = help
        self.description = description
        self.device_id = device_id
        self.mod_only = mod_only
        self.message = message
        self.arguments = arguments
        self.cooldown_in_seconds = cooldown_in_seconds

        mido.set_backend(backend, load=True)


    def is_off_cooldown(self):
        if not self.last_called or not self.cooldown_in_seconds:
            return True
        time_since_call = datetime.datetime.now() - self.last_called
        return time_since_call.seconds > self.cooldown_in_seconds

    async def display_help(self, command, command_trigger, ctx):
        if command == "help":
            message = (
                f"{command_trigger} Help - {self.help}"
                if self.help
                else f"No help available for {self.name}"
            )
            await ctx.reply(content=str(message))
        if command == "description":
            message = (
                f"{command_trigger} Description - {self.description}"
                if self.description
                else f"No description available for {self.name}"
            )
            await ctx.reply(content=str(message))

    def parse_arguments(self, message: str):
        trimmed = message.strip()
        return trimmed.split(" ")

    async def handle_command(self, ctx: commands.Context):
        """Command handler - can be overridden or extended in subclasses"""
        arguments = self.parse_arguments(ctx.message.content[len(ctx.prefix) :])

        command_trigger = arguments.pop(
            0
        )  # remove the argument used to trigger the command
        first_argument = arguments[0]
        if (
            first_argument == self.help_trigger
            or first_argument == self.description_trigger
        ):
            return await self.display_help(first_argument, command_trigger, ctx)

        if not self.is_off_cooldown():
            time_since_call = datetime.datetime.now() - self.last_called
            await ctx.reply(
                content=str(
                    f"Command {self.name} is on cooldown for another {str(self.cooldown_in_seconds - time_since_call.seconds)} seconds."
                )
            )

        # Number of arguments specified in constructor option doesn't match that provided
        # TODO Handle optional values?
        if len(arguments) != len(self.arguments):
            return await ctx.reply(
                content=str(
                    f"Invalid number of arguments! Please specify a single value"
                )
            )

        value = self.message.value

        # Try to validate input sent by user
        # TODO Allow specifying error message format
        if self.message.allow_custom_value:
            for i, argument in enumerate(self.arguments):
                value_provided = arguments[i]
                if argument.validations:
                    for validation in argument.validations:
                        if not validation(value_provided):
                            return await ctx.reply(
                                content=str(
                                    f"Invalid value provided! See {self.name} description for details."
                                )
                            )

        try:
            self.last_called = datetime.datetime.now()
            self.send_midi_message(message=self.message.to_mido_message(value=value))
            self.message.value = value
            await ctx.reply(
                content=str(f"Result: {self.message.to_mido_message(value=value)}")
            )
        except Exception as e:
            await ctx.reply(content=str(f"Error: {e}"))

    def send_midi_message(self, message: mido.Message, debug: bool = False):
        # noinspection PyTypeChecker
        if not self.out_port:
            self.out_port = mido.open_output(self.device_id)
        logger.info(f"Attempting to send {str(message)} on {self.device_id}")
        self.out_port.send(message)


@yaml_info(yaml_tag="MidiControlCommand")
class MidiControlCommand(MidiCommand):
    channel: str
    command_type: MessageType = MessageType.CONTROL_CHANGE
    value: int

    def __init__(self, name: str, **attrs):
        super().__init__(name, **attrs)


class MidiNoteCommand(MidiCommand):
    channel: str
    command_type: MessageType = MidiCommandType.NOTE_ON
    value: int
    duration: int

    def __init__(self, name: str, **attrs):
        super().__init__(name, **attrs)

    def send_midi_message(self, message: mido.Message, debug: bool = False):
        super().send_midi_message(message, debug)
        if self.duration:
            threading.Timer(self.duration, self.send_note_off)

    def send_note_off(self):
        # TODO Add validation around the message type
        self.send_midi_message(self.message.to_mido_message(note_off=True))

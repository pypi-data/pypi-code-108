from typing import List

import mido
from twitchio.ext import commands

from twidi.commands.midi.midi_command import MidiCommand


class EyesyBot(commands.Bot):
    """
    Bot for interacting with Eyesy
    """

    channel = None
    device_id = None
    backend = "mido.backends.pygame"

    def __init__(
        self,
        midi_commands: List[MidiCommand],
        initial_channel: str,
        prefix: str,
        token: str,
        **kwargs,
    ):
        """

        :param midi_commands: A list of MIDI commands
        :param initial_channel: Bot only supports a single channel currently (the owner of the MIDI devices)
        :param kwargs:
        """
        super().__init__(
            token=token, prefix=prefix, **kwargs, initial_channels=[initial_channel]
        )
        mido.set_backend(name=self.backend, load=True)
        for command in midi_commands:
            self.add_command(command)

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")

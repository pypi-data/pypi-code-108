import mido
from mido import Backend

import twidi.config.loader as loader
from twidi.bots.bot import EyesyBot
from twidi.commands import MidiCommand
from twidi import logger


class ConsoleApp:
    config = loader.load_config()
    backend = "mido.backends.pygame"

    def __init__(self):
        mido.set_backend(self.backend, load=True)

    def list_devices(self):
        # noinspection PyTypeChecker
        mido_backend: Backend = mido
        inputs = mido_backend.get_input_names()
        outputs = mido_backend.get_output_names()
        io_ports = mido_backend.get_ioport_names()

        logger.info("Available Inputs:")
        for input in inputs:
            logger.info("\t" + input)

        logger.info("\nAvailable Outputs:")
        for output in outputs:
            logger.info("\t" + output)

        logger.info("\nAvailable IO Ports:")
        for port in io_ports:
            logger.info("\t" + port)

    def update_config(self, config_path=str):
        self.config = loader.load_config(config_path)

    def list_commands(self):
        bot = EyesyBot(midi_commands=self.config.midi_commands, token="", initial_channel="", prefix="")
        logger.info(f'Commands loaded from config: {[str(c) for c in bot.commands.keys()]}')

    def start_bot(self, config_path=None):
        from twidi.bots.bot import EyesyBot

        self.update_config(config_path)
        config_file = self.config
        EyesyBot(
            midi_commands=config_file.midi_commands,
            prefix=config_file.prefix,
            token=config_file.token,
            initial_channel=config_file.channel,
        ).run()

    def test_midi_command(self, command_name: str, value: int, device_id=None):
        config = self.config
        midi_commands = config.midi_commands
        if device_id:
            for command in midi_commands:
                command.device_id = device_id
        bot = EyesyBot(midi_commands=midi_commands, token="", initial_channel="", prefix="")
        # noinspection PyTypeChecker
        command: MidiCommand = bot.get_command(name=command_name)
        message = command.message.to_mido_message(value=value)
        command.send_midi_message(message)

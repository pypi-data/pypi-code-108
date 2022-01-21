"""
Helper functions for debugging MIDI setup during development.
May or may not keep this file on release depending on if it is useful.
"""

import mido
from mido import Backend

from twidi.logger import logger


def log_system_midi_info(backend=None):
    # noinspection PyTypeChecker
    mido_backend: Backend = mido
    mido.set_backend(backend, load=True)
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


def main():
    logger.info("Running MIDI Diagnostic")
    backend = 'mido.backends.pygame'
    log_system_midi_info(backend=backend)

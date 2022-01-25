from terality._terality.globals import global_client
from .data_transfers import DataTransmitterLocal


def switch_to_local_mode():
    """Set up the "local test" configuration for the Terality module.

    Outside of a test or development environment, this method should not be used.
    """
    global_client().set_data_transfer(DataTransmitterLocal())

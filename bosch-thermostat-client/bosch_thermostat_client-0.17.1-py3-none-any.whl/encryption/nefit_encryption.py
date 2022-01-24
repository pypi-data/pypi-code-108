"""Encryption logic of Bosch thermostat."""
from bosch_thermostat_client.const.nefit import MAGIC_NEFIT

from .base_encryption import BaseEncryption


class NefitEncryption(BaseEncryption):
    """Encryption class."""
    magic = MAGIC_NEFIT

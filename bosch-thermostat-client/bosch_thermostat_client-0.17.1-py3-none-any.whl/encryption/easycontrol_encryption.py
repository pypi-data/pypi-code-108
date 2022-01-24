"""Encryption logic of Bosch thermostat."""
from bosch_thermostat_client.const.easycontrol import MAGIC_EASYCONTROL
from bosch_thermostat_client.helper import check_base64
from bosch_thermostat_client.const import VALUE, TYPE
from .base_encryption import BaseEncryption
import json

STRING_VALUE = "stringValue"
FLOAT_VALUE = "floatValue"


class EdgeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        object_type = dct.get(TYPE, None)
        if object_type and VALUE in dct:
            if object_type == STRING_VALUE:
                dct[VALUE] = check_base64(dct[VALUE])
            elif object_type == FLOAT_VALUE:
                dct[VALUE] = float(dct[VALUE])
        return dct


class EasycontrolEncryption(BaseEncryption):
    """Encryption class."""

    magic = MAGIC_EASYCONTROL
    jsondecoder = EdgeDecoder

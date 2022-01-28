"""
Preprocessor used in kaitai struct to decode Base85 (ASCII85) encoded
data
"""
import base64


class B85decode(object):  # pylint: disable=too-few-public-methods
    """
    b85decode preprocessor class
    """
    def __init__(self):
        pass

    def decode(self, in_bindata):  # pylint: disable=no-self-use
        """
        b85decode method
        """
        bindata = bytearray(in_bindata)
        return bytearray(base64.a85decode(bindata))

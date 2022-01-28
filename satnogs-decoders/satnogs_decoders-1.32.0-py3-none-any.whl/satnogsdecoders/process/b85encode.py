"""
Preprocessor used in kaitai struct to encode data into Base85
(ASCII85) encoded data
"""
import base64


class B85encode(object):  # pylint: disable=too-few-public-methods
    """
    b85decode preprocessor class
    """
    def __init__(self):
        pass

    def decode(self, in_bindata):  # pylint: disable=no-self-use
        """
        b85encode method
        """
        bindata = bytearray(in_bindata)
        return bytearray(base64.a85encode(bindata))

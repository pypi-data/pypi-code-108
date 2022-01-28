"""
Preprocessor used in kaitai struct to decode Base64 encoded
data
"""
import base64


class B64decode(object):  # pylint: disable=too-few-public-methods
    """
    b64decode preprocessor class
    """
    def __init__(self):
        pass

    def decode(self, in_bindata):  # pylint: disable=no-self-use
        """
        b64decode method
        """
        bindata = bytearray(in_bindata)
        return bytearray(base64.b64decode(bindata))

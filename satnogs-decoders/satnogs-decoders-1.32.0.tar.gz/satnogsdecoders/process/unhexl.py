"""
Preprocessor used in kaitai struct to encode data into hexl
encoded data
"""
import binascii


class Unhexl(object):  # pylint: disable=too-few-public-methods
    """
    Hexl preprocessor class
    """
    def __init__(self):
        pass

    def decode(self, in_bindata):  # pylint: disable=no-self-use
        """
        unhexl method
        """
        bindata = bytearray(in_bindata)
        return bytearray(binascii.unhexlify(bindata))

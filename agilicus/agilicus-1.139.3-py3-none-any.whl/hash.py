import base64
import binascii
import hashlib
import pathlib


def get_base64_md5(filename):
    hexbytes = hashlib.md5(pathlib.Path(filename).read_bytes()).hexdigest()
    binary_string = binascii.unhexlify(hexbytes)
    return base64.b64encode(binary_string)

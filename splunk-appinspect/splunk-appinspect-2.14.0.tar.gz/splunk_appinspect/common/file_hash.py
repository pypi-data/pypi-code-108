"""
Module to provide high level common functionalities
"""
import hashlib


def md5(file_path):
    """
    generate md5 hash hex string
    """
    return hashlib.md5(_file_as_bytes(open(file_path, "rb"))).hexdigest()


def _file_as_bytes(file):
    with file:
        return file.read()

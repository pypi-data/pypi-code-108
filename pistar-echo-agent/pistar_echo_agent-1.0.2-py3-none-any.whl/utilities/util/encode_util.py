"""
description: this module provides the function get string sha256.
"""
import hashlib


def sha256(*args) -> str:
    """
    Generate a sha256 string from an obj list
    This function is also used to generate
    a fixed folder name from an file case's
    absolute path.
    :return: sha256 string
    """
    result = hashlib.sha256()
    for arg in args:
        part = arg.encode('utf-8')
        result.update(part)
    return result.hexdigest()

"""
description: this module provides parse string functions.
"""
import re


def camel_to_snake(name):
    """
    description: this function is userd to parse camel string to snake string.
    """
    reg = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return reg.sub(r'_\1', name).lower()

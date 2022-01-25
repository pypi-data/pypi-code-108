import time
import sys


def deep_get(obj, path):
    if not path:
        return obj
    elif isinstance(obj, dict):
        return deep_get(obj[path[0]], path[1:])
    elif isinstance(obj, list):
        return [deep_get(child, path) for child in obj]
    else:
        return obj

def uppercase_dict(d):
    """
    Returns a dict with all teh keys, and any child keys uppercased.

    This is used for case insensitive lookups.
    """
    return {
        k.upper(): (uppercase_dict(v) if isinstance(v, dict) else v)
        for k, v in d.items()
    }
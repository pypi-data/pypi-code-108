"""Utility functions."""
from copy import deepcopy


def merge_settings(base: dict, new: dict) -> dict:
    """Return a new dictionary created by merging the settings from ``new`` into ``base``.

    :param base: The base dictionary to merge into
    :type base: ``dict``
    :param new: The new dictionary to merge
    :type new: ``dict``
    :return: A new merged dictionary
    :rtype: ``dict``
    """
    result = {}

    for base_key, base_value in list(base.items()):
        if base_key not in new:
            result[base_key] = deepcopy(base_value)
        else:
            if isinstance(base_value, list):
                result[base_key] = list(base_value + new[base_key])
            elif isinstance(base_value, dict):
                result[base_key] = merge_settings(base_value, new[base_key])
            else:
                result[base_key] = new[base_key]
    for new_key, new_value in list(new.items()):
        if new_key not in base:
            result[new_key] = deepcopy(new_value)
    return result

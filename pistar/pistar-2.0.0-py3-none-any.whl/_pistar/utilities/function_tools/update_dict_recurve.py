"""
description: this module provides the function update_dict.
"""

import collections.abc


def update_dict(updating_dict, resource_dict):
    """
    description: this function is used to update two dictionary recursively.
    """

    if not resource_dict:
        return updating_dict

    for key, value in resource_dict.items():
        if isinstance(value, collections.abc.Mapping):
            updating_dict[key] = update_dict(updating_dict.get(key, {}), value)
        else:
            updating_dict[key] = value

    return updating_dict

from typing import Any, Dict

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


def merge_dict(source_dict: Dict[str, Any], target_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges `source_dict` into `target_dict`.

    All values from `source_dict` will either extend or overwrite
    values in `target_dict`. The merge works recursively. The
    `target_dict` becomes modified.

    Args:
        source_dict (dict): The dict the values should be taken from.
        target_dict (dict): The dict the values should be applied to.

    Returns:
        dict: Returns the modified `target_dict`.
    """
    for key, value in source_dict.items():
        if isinstance(value, dict) and key in target_dict:
            merge_dict(value, target_dict[key])
        else:
            target_dict[key] = value
    return target_dict

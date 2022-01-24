# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" PyTorch utility functions"""
from typing import Any, Dict, Tuple


def intersect_dicts(da: Dict[str, Any], db: Dict[str, Any], exclude: Tuple = (), prefix: str = '') -> \
        Dict[str, Any]:
    """Dictionary intersection of matching keys and shapes, omitting 'exclude' keys, using da values

    :param da: dictionary to select from
    :type da: dict
    :param db: dictionary to filter
    :type db: dict
    :param exclude: keys to exclude
    :type exclude: List
    :param prefix: prefix to add to the keys in db for comparison
    :type prefix: str
    :return: dict intersection
    :rtype: dict
    """
    db_with_prefix = {prefix + k: v for k, v in db.items()}
    return {k: v for k, v in da.items()
            if k in db_with_prefix and not any(x in k for x in exclude) and v.shape == db_with_prefix[k].shape}

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict


def convert_grain_dict_to_str(grain_dict: Dict[str, Any]) -> str:
    """
    Convert dictionary of grains to string.

    Dictionary of the form {key1: value1, key2: value2} will be converted to string
    key1_value1_key2_value2. Additionally string will always be returns in sorted order.
    """
    return "_".join("{}_{}".format(k, v) for k, v in sorted(grain_dict.items(), key=lambda x: str(x[0])))

#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Object memory consumption utilities."""

import typing as t
from typing import List

import numpy as np
from pympler.asizeof import asizeof  # type: ignore


def get_size(obj: t.Any) -> int:
    """Recursively calculates object size in bytes using Pympler library.

    Parameters
    ----------
    obj: object
        Any input object.

    Returns
    -------
    int
        Object size in bytes.
    """
    return int(asizeof(obj))


def print_human_readable_memory(usage: dict) -> None:
    """Convert byte sizes from a dictionary and print a human readable form.

    Parameters
    ----------
    usage: dict

    Returns
    -------
    None
    """
    for k, v in usage.items():
        for unit in ["Bytes", "KB", "MB", "GB"]:
            if v < 1024.0:
                print(f"{k:<20}{np.round(v,decimals=1):<7}{unit}")
                break
            v /= 1024.0


def memory_usage_details(
    obj: t.Any,
    *attr_kw: List[str],
    print_result: bool = True,
    human_readable: bool = True,
) -> dict:
    """TBW.

    Parameters
    ----------
    obj: object
    attr_kw: list
    print_result: bool
    human_readable: bool

    Returns
    -------
    usage: dict

    Raises
    ------
    ValueError
        When no attributes provided.
    AttributeError
        Attribute does not exist in the object.
    """

    usage: dict = {}

    if attr_kw == ():
        raise ValueError("No attributes provided.")

    for attribute in attr_kw[0]:
        if attribute not in obj.__dict__.keys():
            raise AttributeError(
                f"Attribute {attribute} not found in the observed object."
            )

    for key, value in obj.__dict__.items():
        if hasattr(value, "numbytes") and key in attr_kw[0]:
            usage.update({key.replace("_", ""): get_size(value)})

    if print_result:
        if human_readable:
            print_human_readable_memory(usage)
        else:
            print(usage)

    return usage

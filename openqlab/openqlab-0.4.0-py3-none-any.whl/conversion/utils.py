from typing import Tuple

import numpy as np


def base_floor(x: float, base: int = 5) -> int:
    return base * int(np.floor(x / base))


def get_prefix(value: float, tenth_steps: bool = False) -> Tuple[float, str]:
    prefixes = {
        24: "Y",
        21: "Z",
        18: "E",
        15: "P",
        12: "T",
        9: "G",
        6: "M",
        3: "k",
        2: "h",
        1: "da",
        0: "",
        -1: "d",
        -2: "c",
        -3: "m",
        -6: "µ",
        -9: "n",
        -12: "p",
        -15: "f",
        -18: "a",
        -21: "z",
        -24: "y",
    }
    if value == 0.0:
        return value, ""
    exponent = base_floor(np.log10(abs(value)), base=3)
    if -3 <= exponent < 3 and tenth_steps:
        exponent = base_floor(np.log10(abs(value)), base=1)

    if abs(exponent) <= 24:
        value = value * 10 ** -exponent
        return value, prefixes[exponent]
    # if out of range just return the value with no prefix
    return value, ""


def human_readable(value: float, unit: str = "", tenth_steps: bool = False) -> str:
    """
    Return an approximate string representation of a value, with
    appropriate unit prefixes (µ, k, M, ...) added. Accuracy is ~0.1%.

    Parameters
    ----------
    value: :obj:`float`
        the value to convert into human-readable representation
    unit: :obj:`string`
        an optional unit string, such as 'Hz', 'm'

    Returns
    -------
    :obj:`str`
        the human-readable representation
    """
    value, prefix = get_prefix(value, tenth_steps=tenth_steps)

    return f"{value:.4g} {prefix}{unit}"

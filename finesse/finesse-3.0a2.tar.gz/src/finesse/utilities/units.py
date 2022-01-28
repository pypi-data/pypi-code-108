"""Convenience objects and functions for unit manipulation."""

import enum

from .misc import find


@enum.unique
class SI(enum.Enum):
    """Enum defining common SI unit constant names. Look-up
    the corresponding values with the `finesse.utilities.SI_MAP`
    dictionary.

    Examples
    --------
    To get the constant for `SI.MILLI` simply look-up:

    >>> SI_MAP[SI.MILLI]
    1e-3
    """

    YOCTO = 0
    ZEPTO = 1
    ATTO = 2
    FEMTO = 3
    PICO = 4
    NANO = 5
    MICRO = 6
    MILLI = 7
    CENTI = 8
    DECI = 9
    NONE = 10
    KILO = 11
    MEGA = 12
    GIGA = 13
    TERA = 14
    PETA = 15


SI_VALUE = {
    SI.YOCTO: 1e-24,
    SI.ZEPTO: 1e-21,
    SI.ATTO: 1e-18,
    SI.FEMTO: 1e-15,
    SI.PICO: 1e-12,
    SI.NANO: 1e-9,
    SI.MICRO: 1e-6,
    SI.MILLI: 1e-3,
    SI.CENTI: 1e-2,
    SI.DECI: 1e-1,
    SI.NONE: 1.0,
    SI.KILO: 1e3,
    SI.MEGA: 1e6,
    SI.GIGA: 1e9,
    SI.TERA: 1e12,
    SI.PETA: 1e15,
}

SI_LABEL = {
    SI.YOCTO: "y",
    SI.ZEPTO: "z",
    SI.ATTO: "a",
    SI.FEMTO: "f",
    SI.PICO: "p",
    SI.NANO: "n",
    SI.MICRO: "u",
    SI.MILLI: "m",
    SI.CENTI: "c",
    SI.DECI: "d",
    SI.KILO: "k",
    SI.MEGA: "M",
    SI.GIGA: "G",
    SI.TERA: "T",
    SI.PETA: "P",
}


def get_SI_value(name):
    """Get an SI value by name.

    Valid names correspond to the ``values()`` of the ``finesse.utilities.SI_LABEL``
    dict.

    Parameters
    ----------
    name : str
        Label name of the SI value (e.g. "m" for milli, "G" for giga).

    Returns
    -------
    value : float
        Value corresponding to the SI name.
    """
    keys = list(SI_LABEL.keys())
    values = list(SI_LABEL.values())

    idx = find(values, name)
    if idx is None:
        raise ValueError(f"Invalid SI name {name}.")

    key = keys[idx]
    return SI_VALUE[key]

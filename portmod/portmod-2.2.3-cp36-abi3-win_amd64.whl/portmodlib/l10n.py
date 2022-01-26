# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Module with localization helpers"""

import locale
import os
from functools import lru_cache
from typing import List

from portmodlib.portmod import l10n_lookup

# Only used in debug builds of the rust library
_DEBUG_L10N_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "l10n")


@lru_cache()
def _default_locale():
    """Returns the default locale"""
    try:
        locale.setlocale(locale.LC_ALL, "")
        lang, _ = locale.getdefaultlocale()
        if lang is None:
            return "en_GB"
        return str(lang)
    except locale.Error:
        # If default fails, fall back to the C locale, which should hopefully work
        locale.setlocale(locale.LC_ALL, "C")
        return "en_GB"


def l10n(msg_id: str, **kwargs) -> str:
    """
    Wrapper around FluentLocalization.format_value

    Unlike format_value, arguments are passed as keyword arguemnts
    rather than as a dictionary.
    """
    # Get locale before formatting numbers so that LC_ALL gets set properly
    default = _default_locale()

    # TODO: Replace this with fluent formatting when fluent-rs better supports floats
    for key, value in kwargs.items():
        if isinstance(value, float):
            kwargs[key] = f"{value:n}"

    result = l10n_lookup(default, msg_id, kwargs)
    if result:
        return result
    raise RuntimeError(f"No Localization exists for id {msg_id}")


@lru_cache()
def get_locales(separator: str = "-") -> List[str]:
    """Returns detected locales in the form suitable for the repository"""
    locales = []
    parts = _default_locale().replace("-", "_").split("_")
    if len(parts) == 2:
        locales.append(parts[0] + separator + parts[1])
    locales.append(parts[0])
    # Default (lowest priority) is en
    locales.append("en")
    return locales

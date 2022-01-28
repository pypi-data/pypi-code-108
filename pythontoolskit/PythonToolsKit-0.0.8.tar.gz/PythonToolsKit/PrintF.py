#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2021  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

r"""
This package implements tools to build python package and tools.

>>> from PrintF import printf
>>> printf('My message')
[+] My message
>>> printf("My message", state="NOK")
[-] My message
>>> printf("My message", colored=False, state="ERROR")
[!] My message
>>> printf("My message", end="\n\n", state="INFO")
[*] My message

>>> printf("My message", start="\n", state="TODO")

[#] My message
>>> printf("My message", pourcent=20, state="ASK") or print("\n")
[?] My message
[?] 20% |████                |
>>> printf("My message", pourcent=20) or printf("My message", pourcent=55) or print("\n")
[+] My message
[+] 55% |███████████         |
>>> printf("My message", pourcent=20) or print() or printf("My message", pourcent=55) or print("\n")
[+] My message
[+] My message
[+] 55% |███████████         |
>>> printf("My message", add_progressbar=False, pourcent=55) or print("\n")
[+] My message
[+] 55%
>>> printf("My message", oneline_progress=True, pourcent=55) or print()
[+] My message 55% |███████████         |
>>> import PrintF
>>> PrintF.STATES["TEST"] = ("[T]", "\x1b[37m")
>>> printf("My OK message", state="TEST")
[T] My OK message
>>> 
"""

__version__ = "0.0.3"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["printf", "STATES", "COLOR"]

from sys import argv
from typing import Union

STATES = {
    "OK": ("[+]", "\x1b[32m"),
    "NOK": ("[-]", "\x1b[33m"),
    "ERROR": ("[!]", "\x1b[31m"),
    "INFO": ("[*]", "\x1b[34m"),
    "TODO": ("[#]", "\x1b[35m"),
    "ASK": ("[?]", "\x1b[36m"),
}
COLOR = "--no-color" not in argv

states_get = STATES.get


def printf(
    string: str,
    state: str = "OK",
    colored: bool = COLOR,
    pourcent: Union[int, str] = None,
    start: str = "",
    end: str = "\n",
    add_progressbar: bool = True,
    oneline_progress: bool = False,
    **kwargs,
) -> None:

    """
    This function prints colored information.
    """

    show, color = states_get(state)

    if state is None:
        raise ValueError("Invalid state, state should be a key of STATES...")

    if pourcent is not None:

        if oneline_progress:
            progress_bar = f"{pourcent}%"
        else:
            progress_bar = f"{color}{show} {pourcent}%"

        if add_progressbar:
            char = "\u2588"
            progress_state = int(pourcent) // 5
            progress_bar += (
                f" |{char * progress_state}{' ' * (20 - progress_state)}|"
            )
    else:
        progress_bar = ""

    if colored:
        if oneline_progress:
            to_print = (
                f"\x1b[K{start}{color}{show} {string} {progress_bar}"
                f"\x1b[0m{end}\x1b[F"
            )
        else:
            to_print = (
                f"\x1b[K{start}{color}{show} {string}\x1b[0m{end}"
                f"{progress_bar}\x1b[0m\x1b[F"
            )
    else:
        if oneline_progress:
            to_print = f"\x1b[K{start}{show} {string}{progress_bar}{end}\x1b[F"
        else:
            to_print = f"\x1b[K{start}{show} {string}{end}{progress_bar}\x1b[F"

    print(to_print, flush=True, **kwargs, end="")

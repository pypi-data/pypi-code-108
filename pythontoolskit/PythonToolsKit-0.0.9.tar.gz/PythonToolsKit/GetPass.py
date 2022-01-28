#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

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

"""
This package implements tools to build python package and tools.

>>> password = getpass()
Password: ********
>>> password
'password'
>>> password = getpass("Custom: ", "#")
Custom: ########
>>> password
'password'
>>>
"""

__version__ = "0.0.1"
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

__all__ = ["getpass"]

from sys import __stdin__, stdin, stdout
from os import name, device_encoding
from getpass import getpass

flush = stdout.flush
write = stdout.write

if stdin is not __stdin__:

    def getpass(prompt: str = "Password: ", show: str = "*") -> str:
        return getpass(prompt)

elif name == "nt":
    from msvcrt import getch

    encoding = device_encoding(stdin.fileno())
else:
    from termios import TCSADRAIN, tcgetattr, tcsetattr
    from tty import setraw

    fileno = stdin.fileno
    read = stdin.buffer.read
    encoding = device_encoding(fileno())

    def getch() -> bytes:

        """
        This function gets input keyboard and return character.
        """

        fd = fileno()
        tty_attr = tcgetattr(fileno())

        try:
            setraw(fileno())
            char = read(1)
        finally:
            tcsetattr(fd, TCSADRAIN, tty_attr)

        return char


def getpass(prompt: str = "Password: ", show: str = "*") -> str:

    """
    This function prompts for password and show "<show>".
    """

    password = []
    char = None

    no_chars = (
        b"\x00\x01\x02\x03\x04\x05\x06"
        b"\x07\x08\t\n\x0b\x0c\r\x0e\x0f"
        b"\x10\x11\x12\x13\x14\x15\x16\x17"
        b"\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
    )
    newline = b"\r"
    delete = "\b \b"
    delete_char1 = b"\x08"
    delete_char2 = b"\xff"
    ctrlC = b"\x03"

    print(prompt, end="", flush=True)

    while char != newline:
        char = getch()

        if char == delete_char1 or char == delete_char2:
            if password:
                del password[-1]
                write(delete)
                flush()
        elif char == ctrlC:
            raise KeyboardInterrupt
        elif char in no_chars:
            pass
        elif char != newline:
            password.append(char)
            write(show)
            flush()

    print(flush=True)
    return b"".join(password).decode(encoding)

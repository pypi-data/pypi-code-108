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
"""

__version__ = "0.0.2"
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

__all__ = ["Terminal"]

from collections.abc import Callable
from sys import stdout
from enum import Enum

stdout_write: Callable = stdout.write
stdout_flush: Callable = stdout.flush
char_ANSI: str = "\x1b["
char_special_ANSI: str = "\x1b"


class COLORS_MODES(Enum):
    FGCOLOR1 = "3"
    FGCOLOR2 = "9"
    BGCOLOR1 = "4"
    BGCOLOR2 = "10"


class COLORS(Enum):
    BLACK = "0m"
    RED = "1m"
    GREEN = "2m"
    YELLOW = "3m"
    BLUE = "4m"
    MAGENTA = "5m"
    CYAN = "6m"
    GRAY = "7m"


colors = COLORS._member_names_
colors_map = COLORS._member_map_


class Terminal:

    """
    This class implements function to use ANSI console
    characters.
    """

    def change_font(font: int) -> None:

        """
        This function changes font.
        """

        if font > 10:
            raise ValueError(f"font ({font}) should be smaller than 11")

        font += 11
        stdout_write(f"{char_ANSI}{font}m")
        stdout_flush()

    def mode_reverse() -> None:

        """
        This function reverses colors (background/foreground).
        """

        stdout_write(f"{char_ANSI}7m")
        stdout_flush()

    def mode_no_reverse() -> None:

        """
        This function replace colors (background/foreground).
        """

        stdout_write(f"{char_ANSI}27m")
        stdout_flush()

    def mode_underline() -> None:

        """
        This function adds underline.
        """

        stdout_write(f"{char_ANSI}4m")
        stdout_flush()

    def mode_no_underline() -> None:

        """
        This function removes underline.
        """

        stdout_write(f"{char_ANSI}24m")
        stdout_flush()

    def mode_italic() -> None:

        """
        This function adds italic.
        """

        stdout_write(f"{char_ANSI}3m")
        stdout_flush()

    def mode_no_italic() -> None:

        """
        This function removes italic.
        """

        stdout_write(f"{char_ANSI}23m")
        stdout_flush()

    def mode_bold() -> None:

        """
        This function adds bold.
        """

        stdout_write(f"{char_ANSI}1m")
        stdout_flush()

    def mode_no_bold() -> None:

        """
        This function removes bold.
        """

        stdout_write(f"{char_ANSI}21m")
        stdout_flush()

    def mode_intensity() -> None:

        """
        This function adds intensity.
        """

        stdout_write(f"{char_ANSI}2m")
        stdout_flush()

    def mode_no_intensity() -> None:

        """
        This function removes intensity.
        """

        stdout_write(f"{char_ANSI}22m")
        stdout_flush()

    def mode_hide() -> None:

        """
        This function adds hide.
        """

        stdout_write(f"{char_ANSI}8m")
        stdout_flush()

    def mode_no_hide() -> None:

        """
        This function removes hide.
        """

        stdout_write(f"{char_ANSI}28m")
        stdout_flush()

    def mode_default() -> None:

        """
        This function adds bold.
        """

        stdout_write(f"{char_ANSI}0m")
        stdout_flush()

    def change_foreground_color_3bytes(
        red: int, green: int, blue: int
    ) -> None:

        """
        This function changes foreground color
        using the 3 bytes mode.
        """

        if red > 255 or green > 255 or blue > 255:
            raise ValueError(
                f"colors ({red};{green};{blue}) should be in range of 0 to 255"
            )

        stdout_write(f"{char_ANSI}38;2;{red};{green};{blue}m")
        stdout_flush()

    def change_background_color_3bytes(
        red: int, green: int, blue: int
    ) -> None:

        """
        This function changes background color
        using the 3 bytes mode.
        """

        if red > 255 or green > 255 or blue > 255:
            raise ValueError(
                f"colors ({red};{green};{blue}) should be in range of 0 to 255"
            )

        stdout_write(f"{char_ANSI}48;2;{red};{green};{blue}m")
        stdout_flush()

    def change_foreground_color_8bits(color: int) -> None:

        """
        This function changes foreground color
        using the 8 bits mode.
        """

        if color > 255:
            raise ValueError(f"color ({color}) should be in range of 0 to 255")

        stdout_write(f"{char_ANSI}38;5;{color}m")
        stdout_flush()

    def change_background_color_8bits(color: int) -> None:

        """
        This function changes background color
        using the 8 bits mode.
        """

        if color > 255:
            raise ValueError(f"color ({color}) should be in range of 0 to 255")

        stdout_write(f"{char_ANSI}48;5;{color}m")
        stdout_flush()

    def change_foreground_color(color: str, mode: int = 1) -> None:

        """
        This function changes foreground color.
        """

        color = color.upper()

        if mode == 1:
            mode = COLORS_MODES.FGCOLOR1.value
        elif mode == 2:
            mode = COLORS_MODES.FGCOLOR2.value
        else:
            raise ValueError(f"mode ({mode}) sould be 1 or 2")

        if color not in colors:
            raise ValueError(f"color ({color}) should be in {colors}")

        color = colors_map[color].value

        stdout_write(f"{char_ANSI}{mode}{color}m")
        stdout_flush()

    def change_background_color(color: str, mode: int = 1) -> None:

        """
        This function changes background color.
        """

        color = color.upper()

        if mode == 1:
            mode = COLORS_MODES.BGCOLOR1.value
        elif mode == 2:
            mode = COLORS_MODES.BGCOLOR2.value
        else:
            raise ValueError(f"mode ({mode}) sould be 1 or 2")

        if color not in colors:
            raise ValueError(f"color ({color}) should be in {colors}")

        color = colors_map[color].value

        stdout_write(f"{char_ANSI}{mode}{color}m")
        stdout_flush()

    def clean() -> None:

        """
        This function cleans the console.
        """

        stdout_write(f"{char_special_ANSI}c")
        stdout_flush()

    def reset_background() -> None:

        """
        This function resets the background color.
        """

        stdout_write(f"{char_ANSI}39m")
        stdout_flush()

    def reset_foreground() -> None:

        """
        This function resets the foreground color.
        """

        stdout_write(f"{char_ANSI}49m")
        stdout_flush()

    def reset_colors() -> None:

        """
        This function resets colors (background and foreground).
        """

        stdout_write(f"{char_ANSI}0m")
        stdout_flush()

    def start_next_line() -> None:

        """
        This function go to the next line
        (on the first character of the next line).
        """

        stdout_write(f"{char_ANSI}E")
        stdout_flush()

    def precedent_line() -> None:

        """
        This function go to the precedent line
        (keep the same position on the precedent line).
        """

        stdout_write(f"{char_ANSI}A")
        stdout_flush()

    def start_precedent_line() -> None:

        """
        This function go to the precedent line
        (on the first character of the precedent line).
        """

        stdout_write(f"{char_ANSI}F")
        stdout_flush()

    def next_line() -> None:

        """
        This function got to the next line
        (keep the same position on the next line).
        """

        stdout_write(f"{char_ANSI}B")
        stdout_flush()

    def precedent_char() -> None:

        """
        This function go to the precedent character.
        """

        stdout_write(f"{char_ANSI}D")
        stdout_flush()

    def next_char() -> None:

        """
        This function go to the next character.
        """

        stdout_write(f"{char_ANSI}C")
        stdout_flush()

    def start_line() -> None:

        """
        This function go to the start of the line.
        """

        stdout_write(f"{char_ANSI}G")
        stdout_flush()

    def goto(line: int, position: int) -> None:

        """
        This function go to line:position.
        """

        stdout_write(f"{char_ANSI}{line};{position}H")
        stdout_flush()

    def save_position() -> None:

        """
        This function saves the cursor position.
        """

        stdout_write(f"{char_special_ANSI}7")
        stdout_flush()

    def restore_position() -> None:

        """
        This function restore the saved position.
        """

        stdout_write(f"{char_special_ANSI}8")
        stdout_flush()

    def clean_next_line() -> None:

        """
        This function cleans the next line
        (take position on the start of the cleaned line).
        """

        stdout_write(f"{char_ANSI}K")
        stdout_flush()

    def delete_first_line() -> None:

        """
        This function deletes the first line
        (the contents of the rows are moved
        to the previous row).
        """

        stdout_write(f"{char_ANSI}S")
        stdout_flush()

    def add_first_line() -> None:

        """
        This function adds a new empty first line
        (the contents of the rows are moved
        to the next row).
        """

        stdout_write(f"{char_ANSI}T")
        stdout_flush()

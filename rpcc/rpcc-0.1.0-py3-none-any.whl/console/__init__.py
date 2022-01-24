# Copyright 2021-2022, Barcelona Supercomputing Center (BSC), Spain
#
# This software was partially supported by the EuroHPC-funded project ADMIRE
#   (Project ID: 956748, https://www.admire-eurohpc.eu).
#
# This file is part of rpcc.
#
# rpcc is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# rpcc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with rpcc.  If not, see
# <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from rich.console import Console as RichConsole

__all__ = ["console"]

from rpcc.console.highlighter import DiagnosticHighlighter
from rpcc.console.theme import diagnostics_theme


class Console:
    """The main Console class."""

    def __init__(self) -> None:
        """Initialize a `Console` with default options."""
        self.console = RichConsole(highlight=False)
        self.error_console = RichConsole(stderr=True)

    def configure(self, colorize_output: str = "auto") -> None:
        """Reconfigure a `Console`.

        :param colorize_output: Control whether the `Console` should emit ANSI color codes when printing messages.
        The argument accepts either ``"always"``, ``"never"`` or ``"auto"`` (the default).
        """
        ft = {
            "always": True,
            "never": False,
            "auto": None
        }.get(colorize_output, None)

        self.console = RichConsole(force_terminal=ft, highlight=False)
        self.error_console = RichConsole(stderr=True,
                                         theme=diagnostics_theme,
                                         highlighter=DiagnosticHighlighter(),
                                         force_terminal=ft)

    def print(self, *args: Any):
        """Print a message to `stdout`.

        :param args: Objects to print to the terminal.
        """
        self.console.print(*args)

    def eprint(self, *args: Any):
        """Print a message to `stderr`.

        :param args: Objects to print to the terminal.
        """
        self.error_console.print(*args)


# the default console
console = Console()


# ---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to `console`
# ---------------------------------------------------------------------------
def configure(colorize: str = "auto") -> None:
    """Configure the default `console`.

    :param colorize: Control whether the default console should emit ANSI color codes when printing messages.
    The argument accepts either ``"always"``, ``"never"`` or ``"auto"`` (the default).
    """
    console.configure(colorize)


def print(*args: Any) -> None:
    """Print to `stdout` using the default console.

    :param args: The objects to print.
    """
    console.print(*args)


def eprint(*args: Any):
    """Print to `stderr` using the default console.

    :param args: The objects to print.
    """
    console.eprint(*args)

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

from rich.highlighter import RegexHighlighter


class DiagnosticHighlighter(RegexHighlighter):
    """Apply a style to diagnostic messages"""

    base_style = "diagnostic."
    highlights = [
        r"(?P<location>.*?:\d+:\d+:)\s(?P<error>error:)\s(?P<message>.*?)(?:’(?P<ident>.*?)’)?(?P<context>(?:\n.*){2})(?P<caret>\^)\n",
        r"(?P<location>.*?:\d+:\d+:)\s(?P<note>note:)\s(?:’(?P<ident>.*?)’)?(?P<message>.*?)(?P<context>(?:\n.*){2})(?P<caret>\^)\n",
        r"Expected:(?:\n\s+’(?P<token>.*?)’)+"
    ]

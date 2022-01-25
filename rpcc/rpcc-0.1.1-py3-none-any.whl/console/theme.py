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

from rich.theme import Theme

# the colors that should be applied to each part of a diagnostic message
diagnostics_theme = Theme({
    "diagnostic.location": "bold bright_white",
    "diagnostic.error": "bold bright_red",
    "diagnostic.note": "bold cyan",
    "diagnostic.message": "bright_white",
    "diagnostic.context": "default",
    "diagnostic.caret": "bold bright_green",
    "diagnostic.token": "bold bright_cyan",
    "diagnostic.ident": "bold bright_white"
})

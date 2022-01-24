#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import string


def pseudo(value: int = ord('.')) -> str:

    return chr(value)


def _byte_to_printable_non_ws_or_space(value: int,
                                       default: str = '.',
                                       space: str = ' ',
                                       ) -> str:

    s_char = chr(value)

    if s_char in ('\r', '\n'):
        return chr(0x21B5)  # ↵ Downwards Arrow with Corner Leftwards

    if s_char == ' ':
        return space

    if s_char in string.printable and s_char not in string.whitespace:
        return s_char

    return default


def byte_to_compact_printable_with_dots(value: int) -> str:

    s_default = '.'
    s_space = chr(0x22C5)  # ⋅ Dot Operator

    return _byte_to_printable_non_ws_or_space(value, s_default, s_space)


def byte_to_compact_printable_with_frames(value: int) -> str:

    s_default = chr(0x2395)  # ⎕ Apl Functional Symbol Quad
    s_space = chr(0x02FD)  # ⋅˽ Modifier Letter Shelf

    return _byte_to_printable_non_ws_or_space(value, s_default, s_space)

# -------------------------------------------------------------------- #

#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os


def get_cols() -> int:

    try:
        o_size = os.get_terminal_size()
        i_cols = o_size.columns
        # i_lines = o_size.lines
    except OSError:
        i_cols = 80
        # i_lines = 20

    return i_cols

# -------------------------------------------------------------------- #

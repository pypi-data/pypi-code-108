#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from typing import Any, Generator


def indent(steps: int = 0, size: int = 2):
    return ' ' * size * steps


def formatter(unit: Any, indent_steps: int = 0) -> Generator:

    if isinstance(unit, list):
        for index, item in enumerate(unit):

            if not isinstance(item, list) and not isinstance(item, dict):
                yield f'{indent(indent_steps)}[{index}] \'{item}\''
            else:
                yield f'{indent(indent_steps)}[{index}]'
                for subunit in formatter(item, indent_steps + 1):
                    yield subunit

    elif isinstance(unit, dict):
        for key, value in unit.items():
            start = f'{indent(indent_steps)}\'{key}\':'

            if not isinstance(value, list) and not isinstance(value, dict):
                yield f'{start} \'{value}\''
            else:
                yield start
                for item in formatter(value, indent_steps + 1):
                    yield item

    else:
        yield str(unit)

# -------------------------------------------------------------------- #

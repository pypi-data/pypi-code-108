#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from libmonty.outpututils.asciistyling import AsciiColor, AsciiStyle


def display_error_message(error):
    print(AsciiStyle.bold((AsciiColor.red('Error')) + ', ' + error.args[0]))


def error_message(message):
    print(AsciiStyle.bold(AsciiColor.red('Error')) + ', ' + message)


def warning_message(message):
    print(AsciiStyle.bold(AsciiColor.yellow('Warning')) + ', ' + message)


def info_message(message):
    print(AsciiStyle.bold(AsciiColor.blue('Info')) + ', ' + message)

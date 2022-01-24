#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Output decorators with ASCII escape sequences
# Version 1.1

# https://en.wikipedia.org/wiki/ANSI_escape_code

# Python utilites
# https://github.com/sunarch/libmonty
# 'utils' folder


def bold_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[1m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def faint_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[2m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def italic_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[3m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def underlined_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[4m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def blinking_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[5m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def image_negative_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[7m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def primary_font_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[10m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def alternate_font_text(arg_function):
    def new_function(arg_printable, arg_alternate_font_no):
        inserted_no = "1"
        if int(arg_alternate_font_no) in range(1, 10):  # 0 < x < 10 #
            inserted_no = str(arg_alternate_font_no)
        return '\x1b[1{0}m{1}\x1b[0m'.format(inserted_no, arg_function(arg_printable, arg_alternate_font_no))
    return new_function


def black_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[30m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def red_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[31m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def green_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[32m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def yellow_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[33m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def blue_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[34m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def magenta_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[35m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def cyan_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[36m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def white_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[37m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_black_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[40m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_red_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[41m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_green_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[42m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_yellow_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[43m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_blue_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[44m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_magenta_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[45m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_cyan_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[46m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def bg_white_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[47m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def framed_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[51m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def encircled_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[52m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function


def overlined_text(arg_function):
    def new_function(arg_printable):
        return '\x1b[53m{0}\x1b[0m'.format(arg_function(arg_printable))
    return new_function

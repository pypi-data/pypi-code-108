#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

""" Output styling with ASCII escape sequences
    Version 1.1

    https://en.wikipedia.org/wiki/ANSI_escape_code

    Python utilites
    https://github.com/sunarch/libmonty
    'utils' folder
"""


# style ########################################################################

class AsciiStyle:
    """ docstring """

    @staticmethod
    def bold(arg_printable):
        """ docstring """
        return '\x1b[1m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def faint(arg_printable):
        """ docstring """
        return '\x1b[2m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def italic(arg_printable):
        """ docstring """
        return '\x1b[3m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def underlined(arg_printable):
        """ docstring """
        return '\x1b[4m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def blink(arg_printable):
        """ docstring """
        return '\x1b[5m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def image_negative(arg_printable):
        """ docstring """
        return '\x1b[7m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def framed(arg_printable):
        """ docstring """
        return '\x1b[51m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def encircled(arg_printable):
        """ docstring """
        return '\x1b[52m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def overlined(arg_printable):
        """ docstring """
        return '\x1b[53m{0}\x1b[0m'.format(arg_printable)


# font #########################################################################

class AsciiFont:
    """ docstring """

    @staticmethod
    def primary(arg_printable):
        """ docstring """
        return '\x1b[10m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def alternate(arg_printable, arg_alternate_font_no):
        """ docstring """

        inserted_no = '1'

        if int(arg_alternate_font_no) in range(1, 10):  # 0 < x < 10 #
            inserted_no = str(arg_alternate_font_no)

        return '\x1b[1{0}m{1}\x1b[0m'.format(inserted_no, arg_printable)


# color ########################################################################

class AsciiColor:
    """ docstring """

    @staticmethod
    def black(arg_printable):
        """ docstring """
        return '\x1b[30m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def red(arg_printable):
        """ docstring """
        return '\x1b[31m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def green(arg_printable):
        """ docstring """
        return '\x1b[32m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def yellow(arg_printable):
        """ docstring """
        return '\x1b[33m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def blue(arg_printable):
        """ docstring """
        return '\x1b[34m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def magenta(arg_printable):
        """ docstring """
        return '\x1b[35m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def cyan(arg_printable):
        """ docstring """
        return '\x1b[36m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def white(arg_printable):
        """ docstring """
        return '\x1b[37m{0}\x1b[0m'.format(arg_printable)


# background ###################################################################

class AsciiBackground:
    """ docstring """

    @staticmethod
    def black(arg_printable):
        """ docstring """
        return '\x1b[40m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def red(arg_printable):
        """ docstring """
        return '\x1b[41m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def green(arg_printable):
        """ docstring """
        return '\x1b[42m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def yellow(arg_printable):
        """ docstring """
        return '\x1b[43m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def blue(arg_printable):
        """ docstring """
        return '\x1b[44m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def magenta(arg_printable):
        """ docstring """
        return '\x1b[45m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def cyan(arg_printable):
        """ docstring """
        return '\x1b[46m{0}\x1b[0m'.format(arg_printable)

    @staticmethod
    def white(arg_printable):
        """ docstring """
        return '\x1b[47m{0}\x1b[0m'.format(arg_printable)

# END ##########################################################################

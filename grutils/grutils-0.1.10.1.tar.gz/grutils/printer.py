#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .error import Error


class Printer:
    def __init__(self, info_cb=None, err_cb=None):
        self.info_cb = info_cb
        self.err_cb = err_cb


global_printer = Printer()


def print_info(*args):
    s = ' '.join(map(lambda arg: '{}'.format(arg), args))
    if global_printer is None or global_printer.info_cb is None:
        print(s)
    else:
        global_printer.info_cb(s)


def print_err(err: Error, *args):
    s = '{}'.format(err.msg()) + ' '.join(map(lambda arg: '{}'.format(arg), args))
    if global_printer is None or global_printer.err_cb is None:
        print(s)
    else:
        global_printer.err_cb(s)

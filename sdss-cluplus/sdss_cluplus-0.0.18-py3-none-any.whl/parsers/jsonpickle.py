#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-12
# @Filename: jsonpickle.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

'''
'''

from __future__ import annotations

import click
from clu.command import Command
from clu.parsers.click import command_parser

import jsonpickle
import numpy as np


class JsonPickleParamType(click.ParamType):
    name = "jsonpickle"

    def convert(self, value, param, ctx):
        try:
            return jsonpickle.decode(value)
        except ValueError:
            self.fail(f"{value!r} is not a valid jsonpickle", param, ctx)


def pickle(*argv):
    '''
    converts single or multiple data to a quoted json string.
    '''
    if(len(argv) > 1):
        return ["'" + jsonpickle.encode(a, make_refs=False) + "'" for a in argv]
    else:
        return "'" + jsonpickle.encode(argv[0], make_refs=False) + "'"

def unpickle(*argv):
    '''
    converts single or multiple data to a quoted json string.
    '''
    if(len(argv) > 1):
        return [jsonpickle.decode(a[1:-1]) for a in argv]
    else:
        return jsonpickle.decode(argv[0][1:-1])






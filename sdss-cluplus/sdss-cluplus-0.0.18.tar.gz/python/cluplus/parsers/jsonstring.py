#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-12
# @Filename: jsonstring.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

'''
'''

from __future__ import annotations

import click
from clu.command import Command
from clu.parsers.click import command_parser

import json

class JsonStringParamType(click.ParamType):
    name = "jsonstring"

    def convert(self, value, param, ctx):
        try:
            return json.loads(value)
        
        except ValueError:
            self.fail(f"{value!r} is not a valid json string", param, ctx)

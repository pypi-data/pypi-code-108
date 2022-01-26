# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de
# @Date: 2021-07-06
# @Filename: click.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import os

import click
from clu.parsers.click import command_parser


@command_parser.command(name='__commands')
@click.pass_context
def __commands(ctx, command: Command, *args):
    """Returns all commands."""

    # we have to use the help key for the command list, dont want to change the standard model.
    command.finish(help=[k for k in ctx.command.commands.keys() if k[:2] != '__'])


@command_parser.command(name='foo')
@click.pass_context
def foo(ctx, command: Command, *args):
    """Returns all commands."""

    message = []
    for k, v in ctx.command.commands.items():
        if k[:2] == '__': continue
        line = f"{k}("
        for v in v.params:
            line += v.name + ":" + str(v.type).lower()
            if v.default: line += "=" + str(v.default)
            line += "," 
        line += ")"
        message.append(line)

    command.finish(help=message)


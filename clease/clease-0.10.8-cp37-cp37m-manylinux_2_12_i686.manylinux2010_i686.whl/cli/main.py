#!/usr/bin/env python
import click
from clease.version import __version__


@click.group()
@click.version_option(__version__)
def clease_cli():
    """The main CLEASE CLI"""

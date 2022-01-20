#!/usr/bin/env python3
"""This module provides the `register` function for establishing the command-line interface,
and the `run` function to act as the main entry point for the entirety of ntsbuildtools.
"""
from ntsbuildtools.cli.framework import run, register, get_parser, set_version


__all__ = [ 'run', 'register', 'get_parser', 'set_version' ]

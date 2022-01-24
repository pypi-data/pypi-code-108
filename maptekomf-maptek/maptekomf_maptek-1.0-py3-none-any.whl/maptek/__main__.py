"""Provides an entry point to use maptekomf as a program to import data from
an OMF project (file) into a Maptek Project and export data from an Maptek
Project to a OMF project.

This enables:
  python -m maptekomf.maptek import project.omf
  python -m maptekomf.maptek export /scrapbook/project/ --output exported.omf
"""

###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

from .cli import define_parser

if __name__ == '__main__':
    arguments = define_parser().parse_args()
    arguments.command(arguments)

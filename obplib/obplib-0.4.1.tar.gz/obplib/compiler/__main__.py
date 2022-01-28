# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

# Built-in
import os
import math
import logging

# PyPI
import click

# Freemelt
from .. import FileHandler
from . import segment_handler, svg2obp

log = logging.getLogger(__name__)

@click.group()
def OBPC():
    pass

@OBPC.command()
@click.argument('filename')
def compile(**kwargs):
    f0 = kwargs['filename']
    f1 = f0[:-5] + '.obp'
    log.info('Compiling {0} into {1}...'.format(f0, f1))
    blob = FileHandler.get_segment_from_dict(f0)
    if os.path.isfile(f1):
        log.warning('A file named {0} already exists. Would you like to overwrite it? [Y/N]'.format(f1))
        choice = input().lower()
        if choice == 'y':
            FileHandler.write_obp(blob, f1)
        else:
            pass
    elif not os.path.isfile(f1):
        FileHandler.write_obp(blob, f1)

@OBPC.command()
@click.argument('filename')
def decompile(**kwargs):
    f0 = kwargs['filename']
    f1 = f0[:-4] + '.obpj'
    print('Decompiling {0} into {1}...'.format(f0, f1))
    blob = FileHandler.read_obp(f0)
    if os.path.isfile(f1):
        print('A file named {0} already exists. Would you like to overwrite it? [Y/N]'.format(f1))
        choice = input().lower()
        if choice == 'y':
            FileHandler.write_obpj(blob, f1)
        else:
            pass
    elif not os.path.isfile(f1):
        FileHandler.write_obpj(blob, f1)

@OBPC.command()
@click.argument('filename')
def convert(**kwargs):
    f0 = kwargs['filename']
    f1 = f0[:-4] + '.obpj'
    print('Converting {0} into {1}...'.format(f0, f1))
    paths, w, h = svg2obp.read_svg(f0)
    l = svg2obp.convert_svg(paths, w, h)
    FileHandler.write_obpj(l, f1)


@OBPC.command()
@click.argument('filename')
def validate(**kwargs):
    l  = FileHandler.read_obp(kwargs['filename'])
    for seg in l:
        segment_handler.validate_segment(seg)


if __name__ == '__main__':
    OBPC()



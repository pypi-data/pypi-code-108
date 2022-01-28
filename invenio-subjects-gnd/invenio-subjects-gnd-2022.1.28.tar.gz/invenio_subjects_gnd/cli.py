# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022 University of Münster.
#
# invenio-subjects-gnd is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Command line tool."""

import click

from .converter import GNDConverter
from .download import download_gnd
from .reader import GNDReader
from .writer import write_yaml


@click.command()
def main():
    """Generate new subjects_gnd.yaml file."""
    filepath = download_gnd()

    reader = GNDReader(filepath, filter='topics')

    converter = GNDConverter(reader)

    filepath = write_yaml(converter)

    print(f"GND terms written here {filepath}")

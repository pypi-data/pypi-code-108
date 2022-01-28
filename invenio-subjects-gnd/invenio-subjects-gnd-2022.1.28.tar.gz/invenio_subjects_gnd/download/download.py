# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022 University of Münster.
#
# invenio-subjects-gnd is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Download GND file."""

import shutil
from pathlib import Path

import requests


def download_gnd():
    """Download GND file."""
    url = "http://d-nb.info/gnd"
    filename = url.rsplit('/', 1)[-1]
    filepath = Path(__file__).parent / filename

    with requests.get(url, stream=True) as req:
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(req.raw, f)

    return filepath

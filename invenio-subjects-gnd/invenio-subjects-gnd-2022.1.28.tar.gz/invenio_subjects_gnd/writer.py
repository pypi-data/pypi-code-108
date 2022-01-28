# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022 University of Münster.
#
# invenio-subjects-gnd is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""GND subjects_gnd.yaml writer."""

from pathlib import Path

import yaml


def write_yaml(
    entries,
    filepath=Path(__file__).parent / "vocabularies/subjects_gnd.yaml"
):
    """Write the GND yaml file.

    Return filepath to written file.
    """
    with open(filepath, "w") as f:
        yaml.dump(list(entries), f)

    return filepath

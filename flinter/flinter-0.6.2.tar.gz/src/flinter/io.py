"""I/O utilities.

Notes:
    json instead of yaml due to reading/writing performance.

    Indent affects largely the json file.

    yaml loading is kept for backwards compatibility.
"""

import os
import json

import yaml


def dump(filename, db, indent=1):
    with open(filename, 'w') as file:
        json.dump(db, file, indent=indent)


def load(filename):
    ext = os.path.splitext(filename)[-1][1:]

    return MAP2READER[ext](filename)


def _load_json(filename):
    with open(filename, 'r') as file:
        db = json.load(file)

    return db


def _load_yaml(filename):
    with open(filename, "r") as file:
        db = yaml.load(file, Loader=yaml.SafeLoader)

    return db


MAP2READER = {
    'json': _load_json,
    'yaml': _load_yaml,
    'yml': _load_yaml
}

import os
import json

from jeremypy.jeremy_exceptions import JSONFileNotFoundError


def read_json(path, create_if_missing=True):
    """Reads and returns contents of a JSON file."""
    if not os.path.isfile(path):
        if create_if_missing:
            with open(path, 'w') as fp:
                json.dump(None, fp)
                return None
        else:
            raise JSONFileNotFoundError(path)
    else:
        with open(path, 'r') as fp:
            return json.load(fp)


def write_json(path, data):
    """Writes a data object to a JSON file."""
    with open(path, 'w') as fp:
        json.dump(data, fp, indent=4)

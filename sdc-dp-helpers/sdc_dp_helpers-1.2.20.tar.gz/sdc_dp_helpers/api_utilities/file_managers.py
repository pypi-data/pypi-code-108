import json

import yaml


def load_file(file_location, fmt):
    """
    Gathers file data from json or yaml.
    """
    if file_location is not None:
        if fmt in ["yaml", "yml"]:
            with open(file_location, "r") as file:
                config = yaml.safe_load(file)
        elif fmt == "json":
            with open(file_location, "r") as file:
                config = json.load(file)

    return config

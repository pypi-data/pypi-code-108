import json

import yaml


def get_config(configs, fmt):
    """
        Gathers query configurations from json or yaml.
    """
    if configs is not None:
        if fmt in ['yaml', 'yml']:
            with open(configs, 'r') as file:
                config = yaml.safe_load(file)
        elif fmt == 'json':
            with open(configs, 'r') as file:
                config = json.load(file)

    return config

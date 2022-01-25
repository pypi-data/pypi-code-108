import json

from bunch import Bunch


def dict2json(dict_, json_filepath):
    """
    Convert a python dict to a json file.

    Args:
        dict_ (dict): the dict to serialize
        json_filepath (str): path to the json file
    """
    with open(json_filepath, 'w') as json_fp:
        json.dump(dict_, json_fp, indent=4)


def dict2namespace(dict_):
    """
    Convert a python dict to a Bunch namespace.

    Args:
        dict_ (dict): the dict to convert
    Returns:
        (Bunch)
    """
    return Bunch(dict_)


def json2dict(json_filepath):
    """
    Convert `json_filepath` to a python dict.

    Args:
        json_filepath (str): path to the json file
    Returns:
        (dict)
    """
    with open(json_filepath, 'r') as json_fp:
        return json.load(json_fp)


def json2namespace(json_filepath):
    """
    Convert `json_filepath` to a Bunch namespace.

    Args:
        json_filepath (str): path to the json file
    Returns:
        (Bunch)
    """
    return dict2namespace(json2dict(json_filepath))


def Config(**kwargs):
    """
    Shortcut function for creating a config object from keyword arguments.

    Returns:
        (Bunch)
    """
    return dict2namespace(dict(**kwargs))

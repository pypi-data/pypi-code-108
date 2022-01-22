import imp
import os

from twidi import logger


def load_from_file(filepath):
    global py_mod

    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == ".py":
        py_mod = imp.load_source(mod_name, filepath)

    return py_mod


# TODO Arbitrary loading of code is no good
def load_config(config_path=None):
    from twidi.config import config

    config_file = config
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not config_path:
        config_file_path = os.path.join(dir_path, "config.py")
    else:
        config_file_path = os.path.realpath(config_path)
    try:
        loaded_config = load_from_file(config_file_path)
        config_file = loaded_config
    except Exception as e:
        logger.error(f"Invalid config file specified {str(e)}")
    return config_file

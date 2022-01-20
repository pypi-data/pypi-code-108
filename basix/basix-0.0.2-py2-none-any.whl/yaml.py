import yaml
import logging


def read(path):

    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except Exception as err:
            logging.error(err)
            return {}

import logging
from importlib import import_module


def smart_load(conf):
    for key in conf:
        try:
            m = import_module(f'.{key}', package=__name__)
            if hasattr(m, 'load'):
                m.load(conf[key])
        except ModuleNotFoundError as err:
            logging.debug(f'load {key} failed: {err}')


__all__ = ('smart_load',)

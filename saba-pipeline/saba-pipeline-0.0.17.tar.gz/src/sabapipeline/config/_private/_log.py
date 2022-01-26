import logging
from logging import Logger
from types import MethodType

import coloredlogs


def _modify_manager(manager):
    inform_parents = lambda node, child: (
        inform_parents(node.parent, (node if child is None else child)) if node.parent is not None else None,
        node.desc_added(node if child is None else child) if callable(getattr(node, 'desc_added', None)) else None,
        node)[2]
    if not hasattr(manager, "_modified"):
        manager._modified = True
        current_get_logger = manager.getLogger
        manager.getLogger = MethodType(lambda self, name: inform_parents(current_get_logger(name), None), manager)


class MaxHolder:
    def __init__(self, least=0):
        self._val = least

    def update_max(self, new_val):
        if new_val > self._val:
            self._val = new_val
        return self._val


def add_aligned_handler(logger: Logger, colored=True):
    _modify_manager(Logger.manager)
    max_holder = MaxHolder()
    formater = lambda child_name: \
        f'%(asctime)s [%(levelname)-8s] (%(name)-{max_holder.update_max(len(child_name))}s)   %(message)s'
    datefmt = "%Y-%m-%d %H:%M:%S"
    if colored:
        current_handle = [logging.StreamHandler()]
        logger.desc_added = lambda child: (
            logger.removeHandler(current_handle[0]),
            current_handle.remove(current_handle[0]),
            current_handle.append(get_colorful_handler(fmt=formater(child.name), datefmt=datefmt)),
            logger.addHandler(current_handle[0]))
    else:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.desc_added = \
            lambda child: handler.setFormatter(logging.Formatter(fmt=formater(child.name), datefmt=datefmt))
        logger.desc_added(logger)


def get_colorful_handler(fmt: str, datefmt: str) -> logging.Handler:
    logger = logging.getLogger("temp")
    coloredlogs.install(
        level=logging.NOTSET,
        logger=logger,
        field_styles=dict(
            asctime=dict(color='magenta'),
            hostname=dict(color='magenta'),
            levelname=dict(color='magenta', bold=True),
            name=dict(color='magenta'),
            programname=dict(color='magenta'),
            username=dict(color='magenta'),
        ),
        level_styles=dict(
            spam=dict(color='white', faint=True),
            debug=dict(color='white'),
            success=dict(color='white', bold=True),
            verbose=dict(color='white'),
            info=dict(color='cyan'),
            notice=dict(color='magenta'),
            warning=dict(color='yellow'),
            error=dict(color='red', faint=True),
            critical=dict(color='red', bold=True),
        ),
        fmt=fmt,
        datefmt=datefmt
    )
    return logger.handlers[0]


def get_default_logger(logger_name: str) -> Logger:
    result = logging.getLogger(logger_name)
    add_aligned_handler(result)
    result.setLevel(logging.DEBUG)
    logging.getLogger().handlers = result.handlers
    result.propagate = False
    return result

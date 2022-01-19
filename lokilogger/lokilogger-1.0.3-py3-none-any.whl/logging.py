import logging
import logging.config

import pkg_resources

CONFIG_FILE = "config.ini"
CONFIG_FILE_PATH = pkg_resources.resource_filename(__name__, CONFIG_FILE)


def set_log_mode(mode: str) -> None:
    """Set logging mode

    Args:
        mode (str): PROD, DEV or DEV_NO_COLOR
    """
    logging.config.fileConfig(CONFIG_FILE_PATH)
    logger = logging.getLogger()

    prod = logger.handlers[0]
    dev = logger.handlers[1]
    color = logger.handlers[2]

    mode = mode.upper()
    if mode == "PROD":
        logger.removeHandler(dev)
        logger.removeHandler(color)
        logger.info(f"Dev env is set to production")
    elif mode == "DEV_NO_COLOR":
        logger.removeHandler(color)
        logger.removeHandler(prod)
        logger.info(f"Dev env is set to development without colorlog")
    else:
        logger.removeHandler(prod)
        logger.removeHandler(dev)
        if mode != "DEV":
            logger.warning(f"Unrecognized mode, default to development")
        logger.info(f"Dev env is set to development")

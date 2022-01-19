import logging.config

from centaur._.pyvmps.logger._.config import logging_config

logging.config.dictConfig(logging_config)


def get_logger(name):
    return logging.getLogger(name)


if __name__ == "__main__":
    logger = get_logger(__name__)

    # To pass exception information, use the keyword argument exc_info with a true value, e.g.:
    logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
    logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
    logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
    logger.error("Houston, we have a %s", "major problem", exc_info=1)
    logger.exception("Houston, we have a %s", "major problem")
    logger.critical("Houston, we have a %s", "major disaster", exc_info=1)

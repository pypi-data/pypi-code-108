"""Init of automation tool package"""
import logging
logger = logging.getLogger()
is_logger_exist = logging.getLogger().hasHandlers()


def init_logger():
    """ Default logger init with console output handler as default DEBUG level """
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if not is_logger_exist:
    init_logger()


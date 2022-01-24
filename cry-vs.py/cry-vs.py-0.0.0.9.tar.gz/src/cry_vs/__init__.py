import logging
import sys


logger = logging.getLogger(__name__)

if not logging.getLogger().handlers:
    print(
        """---- WARNING ----\n"""
        """This module uses python's built in logging module. Please configure it before using this module.\n"""
        """simply run the following code before importing any other modules:\n\n"""
        """\timport sys\n\timport logging\n\tlogging.basicConfig(encoding="utf-8", stream=sys.stdout, level=logging.INFO)\n\n"""
        """since this has not been configured, cry-vs.py will use a basic configuration.\n"""
        """https://docs.python.org/3/howto/logging.html for more info\n"""
        """---- WARNING------\n"""
    )
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)
    logging.basicConfig(encoding="utf-8", stream=sys.stdout, level=logging.INFO)
    logger.info("logging was not configured, using basic configuration")

else:
    if not logger.hasHandlers():
        for handler in logging.getLogger().handlers:
            logger.addHandler(handler)
    logger.debug("logging is configured")

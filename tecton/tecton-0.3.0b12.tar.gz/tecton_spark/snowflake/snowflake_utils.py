import logging


def supress_snowflake_logs():
    """ Suppress snowflake logs. This is usually needed after an import."""
    logger = logging.getLogger("snowflake")
    logger.setLevel(logging.CRITICAL)

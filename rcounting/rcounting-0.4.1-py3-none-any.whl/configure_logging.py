import logging


def setup(logger, verbose, quiet):
    logger.propagate = False
    logger.handlers.clear()
    logger.setLevel(30 - 10 * (1 - quiet) * (1 + verbose))
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

import logging


def setup_logger(module_name, log_level="INFO"):
    """Logger setup

    Parameters
    ----------
    module_name : str
        Name of the logged model, useful for log traceability
    log_level : str
        Level of logging, either "DEBUG", "INFO", "WARNING" or "ERROR"

    Returns
    -------
    logging.Logger
        Logging object
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)-7s:%(name)-15s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

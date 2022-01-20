import logging


def configure_logging(log_level) -> None:
    numeric_level = getattr(logging, log_level, "INFO")
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=numeric_level)

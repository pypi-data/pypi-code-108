import logging


LEVELS = {name.lower(): value for name, value in logging._nameToLevel.items() if value}


def get_logger(options):
    """
    Configures a logger w/ file/stream handler from settings
    """
    level = LEVELS.get(options.get('log_level') or 'info')
    logger = logging.getLogger('bsync')
    logger.setLevel(level)
    handler = logging.FileHandler(options['log_file']) if options.get('log_file') else logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

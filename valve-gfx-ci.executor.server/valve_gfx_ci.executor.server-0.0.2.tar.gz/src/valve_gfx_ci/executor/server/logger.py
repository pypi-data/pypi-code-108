from logging import getLogger, getLevelName, Formatter, StreamHandler


logger = getLogger(__name__)
logger.setLevel(getLevelName('DEBUG'))
log_formatter = \
    Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] %(funcName)s: "
              "%(message)s")
console_handler = StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

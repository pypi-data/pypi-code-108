from logging import DEBUG, ERROR, Logger, getLogger, root


class Loggable:

    logger: Logger = None

    def _init_logger(self):
        self.logger = getLogger(f'{__name__}.{self.__class__.__name__}')

    def __init__(self):
        self._init_logger()

    def debug(self, *args, **kwargs):
        if root.level <= DEBUG:
            if not self.logger:
                self._init_logger()
            self.logger.debug(*args, **kwargs)

    def error(self, *args, **kwargs):
        if root.level <= ERROR:
            if not self.logger:
                self._init_logger()
            self.logger.error(*args, **kwargs)

import logging

class ServerLogger:
    def debug(self, message, ex=None):
        if ex is None:
            logging.debug(message)
        else:
            logging.debug('%s. Exception: %s' % (message, ex))

    def error(self, message, ex=None):
        if ex is None:
            logging.error(message)
        else:
            logging.exception(message, exc_info=ex)

    def warn(self, message, ex=None):
        if ex is None:
            logging.warning(message)
        else:
            logging.warning('%s. Exception: %s' % (message, ex))

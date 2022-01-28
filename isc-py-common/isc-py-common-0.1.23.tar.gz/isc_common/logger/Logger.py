import logging


class Logger(logging.Logger):
    def logging(self, message, level='info'):
        if level == 'debug':
            self.debug(message)
        elif level == 'warning':
            self.warning(message)
        elif level == 'info':
            self.info(message)
        elif level == 'error':
            self.error(message)

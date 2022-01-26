class LogObfuscator:

    def __init__(self, logger):
        self._replacements = {}
        self._log = logger

    def add_secret_term(self, secret, replacement):
        self._replacements[secret] = replacement

    def __replace(self, msg):
        for secret in self._replacements.keys():
            msg = msg.replace(secret, self._replacements[secret])
        return msg

    def info(self, msg):
        return self._log.info(self.__replace(msg))

    def debug(self, msg):
        return self._log.debug(self.__replace(msg))

    def warning(self, msg):
        return self._log.warning(self.__replace(msg))

    def error(self, msg):
        return self._log.error(self.__replace(msg))

    def exception(self, msg):
        return self._log.exception(self.__replace(msg))

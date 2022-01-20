import logging
import sys
import os

# define global logging format
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)

# define extra log levels
TRACE = 5
logging.addLevelName(TRACE, 'TRACE')


# note: Logger classes should never be instantiated directly
class _BioLibLogger(logging.Logger):

    def __init__(self, name: str, level=logging.INFO):
        super(_BioLibLogger, self).__init__(name=name, level=level)

    def configure(self, default_log_level):
        env_log_level = os.getenv('BIOLIB_LOG')
        if env_log_level is None or env_log_level == '':
            self.setLevel(default_log_level)
        else:
            self.setLevel(env_log_level.upper())

    def setLevel(self, level) -> None:
        try:
            super(_BioLibLogger, self).setLevel(level)
        except ValueError:
            raise Exception(f'Unknown log level "{level}"') from None

        global_root_logger = logging.getLogger()
        # only activate debug logging globally if user selected trace logging
        if self.level == TRACE:
            global_root_logger.setLevel(logging.DEBUG)
        elif self.level == logging.DEBUG:
            global_root_logger.setLevel(logging.INFO)
        else:
            global_root_logger.setLevel(self.level)


def _get_biolib_logger_instance() -> _BioLibLogger:
    # for thread safety use the global lock of logging
    logging._acquireLock()  # type: ignore # pylint: disable=protected-access
    original_logger_class = logging.getLoggerClass()
    try:
        # change logger class temporarily to get instance of _BioLibLogger
        logging.setLoggerClass(_BioLibLogger)
        biolib_logger = logging.getLogger('biolib')
        # change the logger class back to original so we do not interfere with other libraries
        logging.setLoggerClass(original_logger_class)
        return biolib_logger  # type: ignore
    finally:
        logging._releaseLock()  # type: ignore # pylint: disable=protected-access


# expose logger
logger = _get_biolib_logger_instance()

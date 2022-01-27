from rox.core.logging.no_op_logger import NoOpLogger


class Logging:
    instance = None

    @classmethod
    def set_logger(cls, logger):
        cls.instance = logger

    @classmethod
    def get_logger(cls):
        return cls.instance or NoOpLogger()

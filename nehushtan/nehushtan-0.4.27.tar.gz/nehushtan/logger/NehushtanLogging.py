class NehushtanLogging:
    CRITICAL = 50
    FATAL = 50
    ERROR = 40
    WARNING = 30
    WARN = 30
    NOTICE = 25
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    @staticmethod
    def get_label_of_level(level: int):
        if level == NehushtanLogging.DEBUG:
            return 'DEBUG'
        elif level == NehushtanLogging.INFO:
            return 'INFO'
        elif level == NehushtanLogging.NOTICE:
            return 'NOTICE'
        elif level == NehushtanLogging.WARN or level == NehushtanLogging.WARNING:
            return 'WARNING'
        elif level == NehushtanLogging.ERROR:
            return 'ERROR'
        elif level == NehushtanLogging.CRITICAL or level == NehushtanLogging.FATAL:
            return 'CRITICAL'
        else:
            return 'NOTSET'

    @staticmethod
    def get_level_by_label(level_label: str):
        if level_label == 'DEBUG':
            return NehushtanLogging.DEBUG
        elif level_label == 'INFO':
            return NehushtanLogging.INFO
        elif level_label == 'NOTICE':
            return NehushtanLogging.NOTICE
        elif level_label == 'WARN' or level_label == 'WARNING':
            return NehushtanLogging.WARNING
        elif level_label == 'ERROR':
            return NehushtanLogging.ERROR
        elif level_label == 'CRITICAL' or level_label == 'FATAL':
            return NehushtanLogging.CRITICAL
        else:
            return NehushtanLogging.NOTSET

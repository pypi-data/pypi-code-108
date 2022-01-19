from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class LogTagBase:
    def __init__(self, name: str, value: int, color: str = None):
        self.__tag_id__ = id(self)
        self.name = name
        self.alias = ''.join([c.lower() for c in name if c.isalpha()])
        self.value = value
        self.color = color


class LogTagTypes:
    class Debug(LogTagBase):
        def __init__(self, name: str, value: int = 0, color: str = None):
            if 9 < value < 0:
                raise ValueError(f'The log tag "{name}" must have a value between 0 and 9.')
            super().__init__(name=name, value=DEBUG + value, color=color)

    class Info(LogTagBase):
        def __init__(self, name: str, value: int = 0, color: str = None):
            if 9 < value < 0:
                raise ValueError(f'The log tag "{name}" must have a value between 0 and 9.')
            super().__init__(name=name, value=INFO + value, color=color)

    class Warning(LogTagBase):
        def __init__(self, name: str, value: int = 0, color: str = None):
            if 9 < value < 0:
                raise ValueError(f'The log tag "{name}" must have a value between 0 and 9.')
            super().__init__(name=name, value=WARNING + value, color=color)

    class Error(LogTagBase):
        def __init__(self, name: str, value: int = 0, color: str = None):
            if 9 < value < 0:
                raise ValueError(f'The log tag "{name}" must have a value between 0 and 9.')
            super().__init__(name=name, value=ERROR + value, color=color)

    class Critical(LogTagBase):
        def __init__(self, name: str, value: int = 0, color: str = None):
            if 9 < value < 0:
                raise ValueError(f'The log tag "{name}" must have a value between 0 and 9.')
            super().__init__(name=name, value=CRITICAL + value, color=color)


class DefaultLogTags(object):
    def __init__(self):
        self.debug = LogTagTypes.Debug('Debug', color='#1d8ef5')
        self.info = LogTagTypes.Info('Info', color='#17b526')
        self.warning = LogTagTypes.Warning('Warning', color='#a717b5')
        self.error = LogTagTypes.Error('Error', color='#f1a62d')
        self.critical = LogTagTypes.Critical('Critical', color='#f30e0e')

    def __getitem__(self, item) -> LogTagBase:
        try:
            return {
                'debug': self.debug,
                'info': self.info,
                'warning': self.warning,
                'error': self.error,
                'critical': self.critical
            }[item]
        except KeyError:
            raise ValueError(
                'The tag name must be one of "debug", "info", "warning", "error" or "critical".'
            )

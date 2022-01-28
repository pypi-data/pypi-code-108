import logging
from abc import ABCMeta
from inspect import isfunction

from .fields import Fields


__all__ = (
    'Event',
)


class _Record(logging.LogRecord):
    """Need to compare with logging handlers."""

    def __init__(self, msg):

        super().__init__(
            name='', level=10, pathname='', lineno=0,
            msg=msg, args=(), exc_info=None,
        )
        self.msg = msg

    def getMessage(self):
        return self.msg


class EventMetaclass(ABCMeta):

    def __new__(mcs, name, bases, namespace,):
        fields = {}
        excludes = (
            'EMITTERS',
            'SYSLOG_HEADER',
        )

        for base in reversed(bases):
            if issubclass(base, Event) and base != Event:
                fields.update(base.__fields__)

        for attr, value in namespace.items():
            if not attr.startswith('_') and \
                    attr not in excludes and \
                    not isfunction(value):
                fields[attr] = value

        namespace['__fields__'] = fields
        return super().__new__(mcs, name, bases, namespace)


class Event(metaclass=EventMetaclass):

    EMITTERS = (
        logging.StreamHandler(),

    )

    SYSLOG_HEADER = False

    def __init__(self):
        self.fields = Fields(
            syslog_flag=self.SYSLOG_HEADER,
            **self.__fields__,
        )
        self.fields.validate()

    def __call__(self, **fields):
        if fields:
            fields = Fields(
                syslog_flag=self.SYSLOG_HEADER,
                **{**self.fields.all, **fields}
            )
            fields.validate()
            self.emit(fields.render())
        else:
            self.emit(self.fields.render())

    def __repr__(self):
        vals = (f'{key}={value}' for key, value in self.fields.all.items())
        return f'{self.__class__.__name__}({", ".join(vals)})'

    def emit(self, record):
        for emitter in self.EMITTERS:
            emitter.handle((_Record(record)))

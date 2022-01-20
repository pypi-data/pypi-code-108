from collections import namedtuple


class Message:
    SUCCESS = 1
    INFO = 2
    WARNING = 3
    FAILURE = 4
    CRITICAL = 5

    def __init__(self, severity, message):
        self.severity = severity
        self.message = message

    def __eq__(self, other):
        if isinstance(other, Message):
            return (self.severity == other.severity and
                    self.message == other.message)
        else:
            return NotImplemented


class Sequence:
    def __init__(self, description, resolution=None, items=None):
        self.description = description
        self.resolution = resolution
        self.items = (items
                      if items is not None
                      else [])

    def append(self, item):
        self._items.append(item)

    def __eq__(self, other):
        if isinstance(other, Sequence):
            return (self.description == other.description and
                    self.resolution == other.resolution and
                    len(self.items) == len(other.items) and
                    all(map(lambda it: it[0] == it[1],
                            zip(self.items, other.items))))
        else:
            return NotImplemented


class Trace:
    Summary = namedtuple('Summary', ['description', 'exception'])
    Frame = namedtuple('Frame', ['filename', 'linenumber', 'line'])

    def __init__(self, summary, frames):
        self.summary = summary
        self.frames = frames

    def __eq__(self, other):
        if isinstance(other, Trace):
            return (self.summary == other.summary and
                    self.frames == other.frames)
        else:
            return NotImplemented

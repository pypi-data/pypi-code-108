from datetime import datetime

from .immutable import Immutable


class TimestampedImmutable(Immutable):
    def __init__(self):
        self.timestamp = datetime.utcnow().timestamp()  # uuid1 is time based

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp

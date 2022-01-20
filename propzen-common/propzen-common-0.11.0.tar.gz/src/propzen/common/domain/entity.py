from uuid import uuid4, UUID

from .event import Event


class Entity():

    def __init__(self):
        self.id = uuid4()
        self.events = []

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

from typing import TypeVar, Generic, Set

from .entity import Entity

EntityType = TypeVar('EntityType', bound=Entity)


class TrackableRepository(Generic[EntityType]):
    seen: Set[EntityType]

    def __init__(self):
        self.seen = set()

    def track(self, entity: EntityType):
        self.seen.add(entity)

import weakref
from abc import ABCMeta
from collections import namedtuple
from enum import Enum
from typing import Optional

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField

from attune_project_api.items import NotZeroLenStr

StorageItemKeyTuple = namedtuple(
    "StorageItemKeyTuple", ["projectKey", "itemKey"]
)


class ItemStorageGroupEnum(Enum):
    Step = "steps"
    Parameter = "parameters"
    FileArchive = "files"


class StorageMemberTuple(Tuple):
    """Storage Member Tuple

    A storage member tuple is a tuple that is a member of a storage tuple.
     For example.

         class DotTuple(StorageMemberTuple):
             pass

         class Thing2Tuple(StorageTuple):
             myMember:list[DotTuple] = TupleField()

    StorageMemberTuples are required as they store the main parent, not
    the context.

    StorageMemeberTuples can have relations.

    For now, StorageMemberFields can only be one level deep off a StorageTuple

    """

    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
        self.__parentWeakRef = None

    @property
    def storageParent(self) -> Optional["StorageTuple"]:
        return self.__parentWeakRef() if self.__parentWeakRef else None


class StorageTuple(Tuple, metaclass=ABCMeta):
    __group__: ItemStorageGroupEnum = None
    __EXPIRED__ = "expired"

    key: NotZeroLenStr = TupleField(None, jsonExclude=False)

    def __init__(self, **kwargs):
        Tuple.__init__(self, **kwargs)
        self.__ctx = None

    @classmethod
    def niceName(cls) -> str:
        return cls.__name__

    def _bind(self, ctx: "ObjectStorageContext") -> None:
        if self.__ctx is self.__EXPIRED__:
            raise Exception("This tuple is expired and cannot be bound")
        self.__ctx = ctx

        # Tell our member tuples that we're their parent StorageTuple
        for member in [getattr(self, f) for f in self.tupleFieldNames()]:
            # Handle lists and not lists
            if not isinstance(member, list):
                member = [member]
            for listItem in member:
                if isinstance(listItem, StorageMemberTuple):
                    listItem._StorageMemberTuple__parentWeakRef = weakref.ref(
                        self
                    )

    def _unbind(self) -> None:
        self.__ctx = None

    def _expire(self):
        self.__ctx = self.__EXPIRED__

    @property
    def storageIsExpired(self) -> bool:
        return self.__ctx == self.__EXPIRED__

    @property
    def storageContext(self) -> "ObjectStorageContext":
        return self.__ctx

    @property
    def storageProject(self) -> "ContextProjectInfo":
        return self.__ctx.project

    @property
    def storageKeyTuple(self) -> StorageItemKeyTuple:
        return StorageItemKeyTuple(self.__ctx.project.key, self.key)

    @classmethod
    @property
    def storageGroup(cls) -> ItemStorageGroupEnum:
        return cls.__group__

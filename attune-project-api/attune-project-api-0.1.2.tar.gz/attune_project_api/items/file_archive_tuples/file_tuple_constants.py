from enum import Enum


class FileArchiveTupleTypeEnum(Enum):
    VERSIONED = "com.servertribe.attune.tuples.FileArchiveVersionedTuple"
    LARGE = "com.servertribe.attune.tuples.FileArchiveLargeTuple"

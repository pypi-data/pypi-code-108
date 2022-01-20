from dataclasses import dataclass
from typing import List, Union

from strong_typing.auxiliary import CompactDataClass


@dataclass(frozen=True, repr=False)
class Reference(CompactDataClass):
    "Captures a set of columns in a table referenced by a foreign key constraint."

    table: str
    column: Union[str, List[str]]


@dataclass(frozen=True, repr=False)
class PrimaryKey(CompactDataClass):
    "Identifies a set of columns in a table as part of the primary key."

    name: str
    column: Union[str, List[str]]


@dataclass(frozen=True, repr=False)
class ForeignKey(CompactDataClass):
    "Declares a foreign key in a table."

    name: str
    references: Reference

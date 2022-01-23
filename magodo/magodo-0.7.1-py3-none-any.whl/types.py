"""Custom types used by this library."""

from __future__ import annotations

import datetime as dt
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from eris import ErisError, Result
from typist import Comparable


# Type Variables (i.e. `TypeVar`s)
T = TypeVar("T", bound="AbstractTodo")

# Type of a spell function which transforms a line (i.e. a str).
LineSpell = Callable[[str], str]
# Type of the Todo.metadata attribute.
Metadata = Dict[str, Union[str, List[str]]]
# A todo item's priority is always a capital letter.
Priority = Literal[
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
# Type of spell functions used by MagicTodo objects.
TodoSpell = Callable[[T], Result[T, ErisError]]


@runtime_checkable
class AbstractTodo(Comparable, Protocol):
    """Describes how any valid Todo object should look."""

    @classmethod
    def from_line(cls: Type[T], line: str) -> Result[T, ErisError]:
        """Constructs a new Todo object from a string."""

    def to_line(self) -> str:
        """Converts a Todo object back to a string."""

    def new(self: T, **kwargs: Any) -> T:
        """Creates a new Todo using the current Todo's attrs as defaults."""

    @property
    def contexts(self) -> Tuple[str, ...]:  # noqa: D102
        """A todo's contexts.

        A word is normally marked as a context by prefixing it with '@'.
        """

    @property
    def create_date(self) -> Optional[dt.date]:  # noqa: D102
        """The date this todo was created."""

    @property
    def desc(self) -> str:  # noqa: D102
        """A description of this todo."""

    @property
    def done_date(self) -> Optional[dt.date]:  # noqa: D102
        """The date this todo was completed."""

    @property
    def done(self) -> bool:  # noqa: D102
        """Is this todo marked done with an 'x'?"""

    @property
    def metadata(self) -> Metadata:  # noqa: D102
        """A todo's corresponding metadata dictionary.

        A word is metadata if it is of the form KEY:VALUE.
        """

    @property
    def priority(self) -> Priority:  # noqa: D102
        """A todo's priority."""

    @property
    def projects(self) -> Tuple[str, ...]:  # noqa: D102
        """A todo's projects.

        A word is normally marked as a project by prefixing it with '+'.
        """


@runtime_checkable
class AbstractMagicTodo(AbstractTodo, Protocol, Generic[T]):
    """Describes how subclasses of MagicTodoMixin should look."""

    to_line_spells: List[LineSpell]
    from_line_spells: List[LineSpell]
    todo_spells: List[TodoSpell]

    def __init__(self, todo: T) -> None:
        pass

    @classmethod
    def cast_todo_spells(cls, todo: T) -> Result[T, ErisError]:
        """Casts all spells associated with this MagicTodo on `todo`."""

    @classmethod
    def cast_from_line_spells(cls, line: str) -> str:
        """Casts all from_line spells on `line`."""

    def cast_to_line_spells(self, line: str) -> str:
        """Casts all to_line spells on `line`."""

    @property
    def todo(self) -> T:
        """The raw Todo object used by this MagicTodo."""

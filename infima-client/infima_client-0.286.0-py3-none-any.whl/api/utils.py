from typing import Optional, TypeVar, Union

from infima_client.core.types import UNSET, Unset

T = TypeVar("T")


def unwrap_or_unset(given: Optional[T]) -> Union[T, Unset]:
    """Aid mypy in determining union type for if-else clauses."""
    return given if given is not None else UNSET

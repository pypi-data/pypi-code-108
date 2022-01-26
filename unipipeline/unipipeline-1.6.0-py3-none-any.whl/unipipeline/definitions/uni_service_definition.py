from typing import NamedTuple
from uuid import UUID


class UniServiceDefinition(NamedTuple):
    id: UUID
    name: str
    colors: bool
    echo_level: int

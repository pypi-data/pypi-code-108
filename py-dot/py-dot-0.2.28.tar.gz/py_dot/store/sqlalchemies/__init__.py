from enum import Enum
from typing import Any, TypeVar, Dict, Union

from sqlalchemy import text
from sqlalchemy.orm.attributes import History


class Change:
    """ Simplified `History` Structure

    """
    previous_value: Any
    current_value: Any

    def __init__(self, history: History):
        changed = history.has_changes()
        self.changed = changed

        if not changed:
            return

        self.previous_value = history.deleted[0]
        self.current_value = history.added[0]


Changes = Dict[str, Change]


def defaults(value) -> Dict:
    """ Return Column `default` and `server_default` as dict

    Column(String, default='default_value', server_default=text('"default_value"')

    >>> Column(String, **defaults('default_value'))
    """

    if isinstance(value, Enum):
        value = value.value

    return {
        'default': value,
        'server_default': text(
            str(value) if not isinstance(value, str) else f"'{value}'"
        )
    }

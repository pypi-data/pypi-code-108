import logging
from typing import Callable, List, Optional, TypeVar

RESPONSE = TypeVar("RESPONSE")
ITEM = TypeVar("ITEM")
MAX_LIMIT = 1000
MAX_ITEMS = 1000000000
log = logging.getLogger(__name__)


def cursor_multi_request(
    get_cursor: Callable[[RESPONSE], Optional[str]],
    get_items: Callable[[RESPONSE], List[ITEM]],
    limit: Optional[int],
    request: Callable[[Optional[str], Optional[int]], RESPONSE],
) -> List[ITEM]:
    items_left = MAX_ITEMS if limit is None else limit
    if items_left <= 0:
        return []
    output: List[ITEM] = []
    cursor: Optional[str] = None
    while items_left > 0:
        max_limit = min(items_left, MAX_LIMIT)
        response = request(cursor, max_limit)
        items = get_items(response)
        output += items
        items_left -= len(items)
        cursor = get_cursor(response)
        if cursor is None:
            break
    return output

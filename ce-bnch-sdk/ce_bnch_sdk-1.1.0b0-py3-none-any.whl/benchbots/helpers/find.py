from typing import Any, Callable, List, Optional, TypeVar

T = TypeVar("T")


class MultipleMatchesError(Exception):
    pass


def find(objs: List[T], fn: Callable[[T], bool]) -> Optional[T]:
    matches = [obj for obj in objs if fn(obj)]
    if len(matches) > 1:
        raise MultipleMatchesError(f"{len(matches)} matches found.")
    return matches[0] if matches else None


def find_by_id_or_name(objs: List[Any], id_or_name: str) -> Optional[Any]:
    return find(objs, lambda o: o.id == id_or_name or o.name.strip() == id_or_name)

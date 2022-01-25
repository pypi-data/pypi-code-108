import ast
from typing import Callable, Any, Optional, Type, TypeVar, List
from functools import wraps

__all__ = [
    'acceptNone',
    'classproperty',
    'identity',
    'splitNestedString'
]


T = TypeVar('T')


def acceptNone(func: Callable[[Any], Any]) -> Callable[[Optional[Any]], Any]:
    @wraps(func)
    def wrapper(x: Optional[Any]) -> Any:
        if x is None:
            return None

        return func(x)
    return wrapper


def identity(x: T) -> T:
    return x


class classproperty:
    """Much like property except only allows for a gettter and works like a classmethod. No instances needed!"""
    def __init__(self, func: Callable[[Type[Any]], Any]) -> None:
        self.func = func

    def __get__(self, _: Any, owner: Type[Any]) -> Any:
        return self.func(owner)


def splitNestedString(arraystring: Optional[str]) -> List[str]:
    """Parses a string from psycopg array/composite type into a list"""
    # Return empty list for null values
    if arraystring is None:
        return []

    itemstring = arraystring[1:-1]  # Cut off {}

    escaped = False

    inString = False

    depth = 0

    items = []
    startingIndex = 0

    for i, c in enumerate(itemstring):
        if c == ',' and not inString and depth == 0:
            items.append(itemstring[startingIndex:i])
            startingIndex = i + 1

        if escaped:
            escaped = False
        else:
            if c == '"':
                inString = not inString
            elif c == '\\':
                escaped = True

            # Handle multi-dimensional array strings
            if not inString:
                if c == '{' or c == '(':
                    depth += 1
                elif c == '}' or c == ')':
                    depth -= 1

    items.append(itemstring[startingIndex:])

    for i, item in enumerate(items):
        if item[0] == '"':
            items[i] = ast.literal_eval(item)  # Safely eval strings

    return items

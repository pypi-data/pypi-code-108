from typing import Dict, Any

from py_dot.core.strings import to_snake


def assign(target: Dict, source: Dict):
    # Todo: using `|` operator for over 3.9
    return {
        **target,
        **source
    }


def merge(target: Dict, source: Dict) -> Dict:
    """ Merge Multiple Dict to Single Dict

    >>> merge({1: [1]}, {1:[2]})
    ... {1: [1, 2]}
    """
    result = {**target}

    for name in source:
        source_value = source[name]
        if name not in result:
            result[name] = source_value
            continue

        target_value = result[name]

        if isinstance(source_value, dict):
            if isinstance(target_value, dict):
                result[name] = merge(target_value, source_value)
                continue

        if isinstance(source_value, list):
            if isinstance(target_value, list):
                result[name] = [*target_value, *source_value]
                continue

        result[name] = source_value

    return result


def to_snake_key(values: Dict[str, Any]) -> Dict:
    snake_values = {}

    for name in values:
        snake_values[to_snake(name)] = values[name]

    return snake_values

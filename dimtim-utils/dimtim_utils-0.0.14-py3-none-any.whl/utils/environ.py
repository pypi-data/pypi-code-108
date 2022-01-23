from typing import Optional, Type, Union


def to_bool(value: Union[str, int, bool]) -> bool:
    if isinstance(value, str):
        return value.lower() in ('true', 't', '1')
    return bool(value)


def to_int(value: Union[str, int], default: int = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_list(value: str, cast: Type = None, separator: str = ',') -> list[str]:
    result = []
    if isinstance(value, str):
        result = [v for v in value.split(separator) if v]
    return [cast(v) for v in result] if callable(cast) else result

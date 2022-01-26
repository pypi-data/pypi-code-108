from typing import Union


def strip_filter(value: Union[str, None]) -> Union[str, None]:
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value

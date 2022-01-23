from typing import Sequence


def chunked(value: Sequence, size: int):
    for i in range(0, len(value), size):
        yield value[i:i + size]

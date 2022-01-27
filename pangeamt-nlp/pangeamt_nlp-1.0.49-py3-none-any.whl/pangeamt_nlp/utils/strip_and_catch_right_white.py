from pangeamt_nlp.utils.strip_and_catch_left_white import strip_and_catch_left_white
from typing import Tuple


def strip_and_catch_right_white(text: str) -> Tuple[str, str]:
    a, b = strip_and_catch_left_white(text[::-1])
    return a[::-1], b[::-1]

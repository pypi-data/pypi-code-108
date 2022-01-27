from typing import Tuple
from pangeamt_nlp.utils.strip_and_catch_left_white import strip_and_catch_left_white
from pangeamt_nlp.utils.strip_and_catch_right_white import strip_and_catch_right_white


def strip_and_catch_white(text: str) -> Tuple[str, str, str]:
    text, left = strip_and_catch_left_white(text)
    text, right = strip_and_catch_right_white(text)
    return text, left, right

from typing import Tuple


def strip_and_catch_left_white(text: str) -> Tuple[str, str]:
    left_white = ''
    for char in text:
        if char.isspace():
            left_white += char
        else:
            break
    return text[len(left_white):], left_white

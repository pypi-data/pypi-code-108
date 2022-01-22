import random
import secrets
import string
from typing import Sequence

from dimtim.utils.data.wordlists import ADJECTIVES, NOUNS

DEFAULT_CHARSET = string.ascii_letters + string.digits
PASSWORD_CHARSET = DEFAULT_CHARSET + string.punctuation
UPPER_CHARSET = string.ascii_uppercase + string.digits
HEX_CHARSET = string.hexdigits


def get_random_string(length: int, charset: str = DEFAULT_CHARSET):
    return ''.join(secrets.choice(charset) for _ in range(length))


def string4():
    return get_random_string(4, DEFAULT_CHARSET)


def string8():
    return get_random_string(8, DEFAULT_CHARSET)


def string16():
    return get_random_string(16, DEFAULT_CHARSET)


def string32():
    return get_random_string(32, DEFAULT_CHARSET)


def string64():
    return get_random_string(64, DEFAULT_CHARSET)


def hex4():
    return get_random_string(4, HEX_CHARSET)


def hex8():
    return get_random_string(8, HEX_CHARSET)


def hex16():
    return get_random_string(16, HEX_CHARSET)


def hex32():
    return get_random_string(32, HEX_CHARSET)


def hex64():
    return get_random_string(64, HEX_CHARSET)


def string8upper():
    return get_random_string(8, UPPER_CHARSET)


def username(underscores: bool = True):
    if underscores:
        return f'{random.choice(ADJECTIVES)}_{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}'
    return f'{random.choice(ADJECTIVES).capitalize()}{random.choice(ADJECTIVES).capitalize()}{random.choice(NOUNS).capitalize()}'


def choice(variants: Sequence):
    return random.choice(variants)

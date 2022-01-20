import string
import random


def check_type(v, t, m):
    if not isinstance(v, t):
        raise TypeError(m)


def unique_string(n=20):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))

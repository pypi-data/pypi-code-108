from random import sample


def randompuncs() -> str:
    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    punctuation = r"""!#$%&()*+,-./:;<=>?@[\]^_`{|}~"""
    digits = '0123456789'
    ascii_letters = ascii_lowercase + ascii_uppercase
    return ''.join(sample(punctuation+ascii_letters+digits, 24))


def env_content() -> str:
    return f"""
OPERATOR_SECRET_KEY="{randompuncs()}"
    """.strip() + "\n"

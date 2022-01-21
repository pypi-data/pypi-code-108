import re


def camelcase(string):
    """ Convert string into camel case.
    Args:
        string: String to convert.
    Returns:
        string: Camel case string.
    """

    string = re.sub(r"^[\-_\.]", '', str(lowercase(string)))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(r"[\-_\.\s]([a-z])", lambda matched: uppercase(matched.group(1)), string[1:])


def snakecase(string):
    """Convert string into snake case.
    Join punctuation with underscore
    Args:
        string: String to convert.
    Returns:
        string: Snake cased string.
    """

    string = re.sub(r"[\-\.\s]", '_', str(string))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(r"[A-Z]", lambda matched: '_' + lowercase(matched.group(0)), string[1:])


def uppercase(string):
    """Convert string into upper case.
    Args:
        string: String to convert.
    Returns:
        string: Uppercase case string.
    """

    return str(string).upper()


def lowercase(string):
    """Convert string into lower case.
    Args:
        string: String to convert.
    Returns:
        string: Lowercase case string.
    """

    return str(string).lower()

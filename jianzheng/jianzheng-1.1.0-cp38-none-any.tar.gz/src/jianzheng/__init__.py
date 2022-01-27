from . import base


__version__ = "1.1.0"


def setup() -> bool:
    """
    This function checks if current environment supports using jianzheng.

    Returns:
        True when current environment supports using jianzheng.

    Raises:
        1. jianzheng.base.exceptions.InvalidEnvironmentPath:
            Environment absolute path has chracters out of ASCII printable characters(decimal 32 ~ 126).

    Example:
        import jianzheng
        jianzheng.setup()

    Use this function when the first time to import jianzheng into your project for cheking if current environment supports using jianzheng!
    """

    # Temp package importing
    from os import getcwd

    # Absolute path cheking
    absolute_path = _absolute_path = getcwd()
    for d in range(32, (126 + 1)):
        _absolute_path = _absolute_path.replace(chr(d), "")
    if _absolute_path:
        raise base.exceptions.InvalidEnvironmentPath(absolute_path)

    # No problems
    print(f"Welcome to use jianzheng {__version__}!")

    return True

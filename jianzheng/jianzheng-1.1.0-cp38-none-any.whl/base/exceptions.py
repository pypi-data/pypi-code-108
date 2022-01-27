
class EnvironmentError(Exception):
    """
    Current environment does't surport to use jianzheng.

    Args:
        error_type: The class constants that defined below.
        **kwargs: Special arguments you can give in the following ways:
            1) error_type == EnvironmentError.PATH_CHARACTERS_OUT_OF_ASCII_PRINTABLE_CHARACTERS == 1:
                current_path: Current environment absolute path.

    Examples:
        import jianzheng
        1) error_type == EnvironmentError.PATH_CHARACTERS_OUT_OF_ASCII_PRINTABLE_CHARACTERS == 1:
            raise EnvironmentError(EnvironmentError.PATH_CHARACTERS_OUT_OF_ASCII_PRINTABLE_CHARACTERS, current_path="~/όραμα")

    You don't need to raise this error manually because jianzheng.setup() will do all the checking and raise errors if current environment has some problems.
    """

    # Error types
    PATH_CHARACTERS_OUT_OF_ASCII_PRINTABLE_CHARACTERS = 1

    def __init__(self, error_type: int, **kwargs: object) -> None:
        self.error_type = error_type
        self.kwargs = kwargs
        super().__init__()


class InvalidEnvironmentPath(EnvironmentError):
    """
    Some characters in environment absolute path are out of ASCII printable characters.

    Args:
        current_path: Current environment absolute path.

    Excamples:
        import jianzheng
        raise jianzheng.base.exceptions.InvalidEnvironmentPath("~/όραμα")

    You don't need to raise this error manually because jianzheng.setup() will do all the checking and raise errors if current environment has some problems.
    """

    def __init__(self, current_path: str) -> None:
        self.current_path = current_path
        super().__init__(error_type=super(
        ).PATH_CHARACTERS_OUT_OF_ASCII_PRINTABLE_CHARACTERS)

    def __str__(self) -> str:
        return f"Environment absolute path does't allowed to have chracters out of ASCII printable characters(decimal 32 ~ 126). (Current: {self.current_path})"

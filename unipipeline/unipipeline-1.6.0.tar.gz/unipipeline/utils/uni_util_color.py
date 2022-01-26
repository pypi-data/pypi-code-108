class UniUtilColor:
    COLOR_MAGENTA = '\u001b[35m'
    COLOR_YELLOW = '\u001b[33m'
    COLOR_GREEN = '\u001b[32m'
    COLOR_WHITE = '\u001b[37m'
    COLOR_BLACK = '\u001b[30m'
    COLOR_GRAY = '\u001b[0;37m'
    COLOR_BLUE = '\u001b[34m'
    COLOR_CYAN = '\u001b[36m'
    COLOR_RED = '\u001b[31m'

    COLOR_RESET = '\u001b[0m'

    def __init__(self, enabled_colors: bool = True) -> None:
        self._enabled = enabled_colors

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def color_it(self, color: str, text: str) -> str:
        return f'{color}{text}{self.COLOR_RESET}' if self._enabled else text

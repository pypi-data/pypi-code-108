"""Game tiles."""

from dataclasses import dataclass
from enum import Enum, auto

from colorama import Back, Cursor, Fore, Style as AnsiStyle

from . import game

_ROWS = 3
_COLUMNS = 5
_PADDING = 0

class Position(Enum):
    """How to position a tile when printing it."""

    STANDALONE = auto()
    FIRST_PRINT = auto()
    EDIT = auto()

    def begin(self, round_: int, index: int, row: int) -> str:
        """Get the string that begins the positioning."""
        cls = self.__class__

        if self == cls.STANDALONE:
            return ''

        if self == cls.FIRST_PRINT:
            if index == 0:
                if round_ == 0 or row != 0:
                    return ''

                return '\n' * _PADDING

            # pylint: disable=invalid-name
            up = Cursor.UP(_ROWS - row)
            forward = Cursor.FORWARD((_COLUMNS + _PADDING) * index)
            return f'{up}{forward}'

        if self == cls.EDIT:
            # pylint: disable=invalid-name
            up = Cursor.UP(((_ROWS + _PADDING) * (game.ROUNDS - round_)) - _PADDING - row)
            # FIXME: Why do we need the extra FORWARD and BACK?
            forward = Cursor.FORWARD(((_COLUMNS + _PADDING) * index) + 1)
            back = Cursor.BACK()
            return f'{up}{forward}{back}'

        raise ValueError(f"unhandled position: {self.name}")

    def end(self, round_: int, index: int, row: int) -> str:
        """Get the string that ends the positioning."""
        cls = self.__class__

        if self == cls.STANDALONE:
            return '\n'

        if self == cls.FIRST_PRINT:
            if index == 0:
                return '\n'

            down = Cursor.DOWN(_ROWS - row)
            back = Cursor.BACK((_COLUMNS * (index + 1)) + (_PADDING * index))
            return f'{down}{back}'

        if self == cls.EDIT:
            down = Cursor.DOWN(((_ROWS + _PADDING) * (game.ROUNDS - round_)) - _PADDING - row)
            back = Cursor.BACK(((_COLUMNS + _PADDING) * (index + 1)) - _PADDING)
            return f'{down}{back}'

        raise ValueError(f"unhandled position: {self.name}")

class Style(Enum):
    """Style in which to print a tile."""

    INPUT = auto()
    CORRECT = auto()
    MISPLACED = auto()
    ABSENT = auto()

    def __str__(self) -> str:
        cls = self.__class__

        if self == cls.INPUT:
            return Fore.WHITE + Back.BLACK

        if self == cls.CORRECT:
            return Fore.BLACK + Back.GREEN

        if self == cls.MISPLACED:
            return Fore.BLACK + Back.YELLOW

        if self == cls.ABSENT:
            return AnsiStyle.DIM + Fore.WHITE + Back.BLACK

        raise ValueError(f"unhandled style: {self.name}")

@dataclass
class Tile:
    """A printable tile representing a single letter."""

    round_: int
    index: int
    letter: str = ' '
    position: Position = Position.STANDALONE
    style: Style = Style.INPUT

    def __post_init__(self):
        self.letter = self.letter.upper()

    def __str__(self) -> str:
        begin = lambda row: self.position.begin(self.round_, self.index, row)
        end = lambda row: self.position.end(self.round_, self.index, row)

        return (
            f"{begin(0)}{self.style}┌─{'─'        }─┐{AnsiStyle.RESET_ALL}{end(0)}"
            f"{begin(1)}{self.style}│ {self.letter} │{AnsiStyle.RESET_ALL}{end(1)}"
            f"{begin(2)}{self.style}└─{'─'        }─┘{AnsiStyle.RESET_ALL}{end(2)}"
        )

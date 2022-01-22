"""User interface."""

from typing import Literal, Union

import colorama
from tap import Tap

from .game import Game

class _ArgumentParser(Tap):
    word: str = 'today\'s'  # which word to make the answer
    day: Union[Literal['today'], int] = 'today'  # which day to use for today's word
    bot: bool = False  # have the bot play instead

    def configure(self):
        self.add_argument('-w', '--word')
        self.add_argument('-d', '--day', type=lambda day: day if day == 'today' else int(day))
        self.add_argument('-b', '--bot')

def cli():
    """Command-line interface."""
    args = _ArgumentParser(description="Interact with Wordle.").parse_args()

    colorama.init()
    Game(answer=args.word, day=args.day, bot=args.bot).play()

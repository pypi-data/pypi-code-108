"""Game player interface and implementations."""

from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Thread
from time import sleep

from sshkeyboard import listen_keyboard, stop_listening

from ..common.hint import Hint
from ..common.words import LENGTH
from . import game
from .guess import filter_guesses, score_strings, sort_guesses

class Player(metaclass=ABCMeta):
    """A player of the game."""

    @abstractmethod
    def start_guess(self, round_: int, hint: Hint) -> None:
        """Start a new guess.

        :param round_: the round that's starting
        :param hint: the hint resulting from the previous guess
        """

    @abstractmethod
    def output_key(self, index: int) -> str:
        """Output a key for the current guess.

        If it's
        - a letter, then it'll be appended to the guess at the given index.
        - a backspace, then the last letter guessed will be deleted.
        - an enter, then the current guess will be submitted.
        """

    @abstractmethod
    def stop_guess(self, round_: int) -> None:
        """Conclude the current guess; it has been submitted.

        :param round_: the round that finished
        """

class User(Player):
    """A human—or chimpanzee… maybe even a corvid?—player."""

    def __init__(self):
        self._thread: Thread = None
        self._queue: Queue[str] = Queue()

    def start_guess(self, round_: int, hint: Hint) -> None:
        if round_ == 0:
            self._start_listening()

    def output_key(self, index: int) -> str:
        return self._queue.get()

    def stop_guess(self, round_: int) -> None:
        if round_ == game.ROUNDS - 1:
            self._stop_listening()

    def _start_listening(self) -> None:
        """Start listening to the user's keyboard in a new thread."""
        self._thread = Thread(
            target=listen_keyboard,
            kwargs={
                'on_press': self._handle_keypress,
                'delay_second_char': 0.05,
            },
            daemon=True,
        )
        self._thread.start()

    def _stop_listening(self) -> None:
        """Stop listening to the user's keyboard."""
        stop_listening()

    def _handle_keypress(self, key: str) -> None:
        """Handle the user's input."""
        self._queue.put(key)

class Bot(Player):
    """A bot: No I/O is required; it guesses on its own."""

    def __init__(self):
        self._possible_guesses: set[str] = filter_guesses(Hint())
        self._guess: str = None

    def start_guess(self, round_: int, hint: Hint) -> None:
        self._possible_guesses &= filter_guesses(hint)
        sorted_guesses = sort_guesses(self._possible_guesses, score_strings())

        self._guess = sorted_guesses[0]
        self._possible_guesses.remove(self._guess)
        # Pause for effect
        sleep(1)

    def output_key(self, index: int) -> str:
        # Pause for effect
        sleep(0.25)
        return 'enter' if index == LENGTH else self._guess[index]

    def stop_guess(self, round_: int) -> None:
        pass

import os
from collections import Counter, defaultdict
from contextlib import suppress

import numpy as np
from rich import print
from rich.panel import Panel
from rich.prompt import Confirm, Prompt


def filter_array(filter_func, words) -> np.ndarray:
    return np.array(list(filter(filter_func, words)))


def filter_words(words, letters, pos) -> np.ndarray:
    for char in letters:
        if pos == 0:  # not inside
            words = filter_array(lambda x: x.find(char) == -1, words)
        elif pos >= 1 and pos <= 5:  # known position
            words = filter_array(lambda x: x[pos - 1] == char, words)
        elif pos < 0:  # known not position
            words = filter_array(lambda x: x.find(char) != -1, words)
            words = filter_array(lambda x: x[-pos - 1] != char, words)
    return words


def get_words() -> np.ndarray:
    # Get data
    filepath = os.path.join(os.path.dirname(__file__), "data/popular_filtered.txt")
    # filepath = os.path.join(os.path.dirname(__file__), "data/words_filtered.txt")
    return np.loadtxt(filepath, dtype="str")


def print_help() -> None:
    print(
        Panel(
            "Help (?) [bold blue]position[/]: "
            + "([bold green]green[/]): 1 to 5, "
            + "([bold]black[/]): 0, "
            + "([bold yellow]yellow[/]): -1 to -5"
        )
    )


def format_guess(guess) -> str:
    formated_guess = ""
    for char in guess:
        if char.isalpha():
            formated_guess += f"[bold white on green]{char.upper()}[/]"
        else:
            formated_guess += f"{char}"

    return f"{formated_guess}"


def find_most_frequent_letters(words, n=4) -> list:
    # Count letters
    letters: dict = defaultdict(int)
    for word in words:
        for k, v in Counter(word).items():  # type: str, int
            letters[k] += v
    sorted_keys = sorted(letters.items(), key=lambda kv: kv[1], reverse=True)

    return [kv[0] for kv in sorted_keys[:n]]


def find_most_representative_words(words, n=4) -> list:
    most_freq_letters = find_most_frequent_letters(words, n)
    sub_list = []
    for word in words:
        if all(char in word for char in most_freq_letters):
            sub_list.append(word)
    return sub_list[:n]


def cli() -> None:

    # Init by parsing wordlist
    words = get_words()

    # Helper
    print_help()

    guess = "12345"

    with suppress(KeyboardInterrupt):
        while True:
            # Print best guess words
            print(f"Best guess: ({find_most_representative_words(words)})")

            # Get user input to filter words
            raw_input = Prompt.ask(
                f"Guess word ({format_guess(guess)}) "
                + "[bold][[red]<letter(s)>[/red] [blue]<position>[/blue]][/]"
            )
            if raw_input[0] == "?":
                print_help()
                continue
            else:
                # Parse input
                letters, pos_str = raw_input.split(" ")
                pos = int(pos_str)
                # Filter words
                words = filter_words(words, letters, pos)
                if pos > 0:
                    guess = guess[: pos - 1] + letters[0] + guess[pos:]

            # Print status
            if len(words) == 1:
                guess = words[0]
                print(Panel(f"Solution: [bold green]{guess}[/] :partying_face:"))
                break

            elif len(words) == 0:
                print("Failed!", ":sob:")

                restart = Confirm.ask("Restart guess?")
                if restart:
                    words = get_words()
                    guess = "12345"
                else:
                    break

            else:
                print("Possible words:", words)


if __name__ == "__main__":
    cli()

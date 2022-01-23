# sample-bot.py

# sample bot to play wordle. see wordle.py for how to play.
import random


# this has lots of false positives, only pay attention to 3s
#
def could_match(target, guess, feedback):
    for i, ch in enumerate(feedback):
        if "3" == ch:
            if target[i] != guess[i]:
                return False
        else:
            if target[i] == guess[i]:
                return False
    return True


class Bot:
    def __init__(self, wordlist):
        self._allowed_answers = [k for k, v in wordlist.items() if v]

    def __call__(self, state):
        # state looks like: "-----:00000,arose:31112,amend:31211"
        possible = self._allowed_answers
        for pair in state.split(","):
            guess, feedback = pair.split(":")
            possible = list(filter(lambda x: could_match(x, guess, feedback), possible))
        return random.choice(possible)

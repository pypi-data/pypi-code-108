"""Logic for making guesses."""

import string

from ..common import words
from ..common.hint import Hint

LetterScores = dict[str, int]
WordScores = list[LetterScores]

def filter_guesses(hint: Hint) -> set[str]:
    """Get all possible guesses according to the given hint."""
    filtered_guesses: set[str] = set()
    for word in words.possible_words:
        for index, letter in enumerate(word):
            if letter in hint.absent \
                    and word.count(letter) != len(hint.correct.get(letter, set())) \
                                            + len(hint.misplaced.get(letter, set())):
                # This letter is absent in the answer, so this is not a
                # possible guess
                break

            if hint.inverse_correct.get(index, letter) != letter \
                    or letter in hint.inverse_misplaced.get(index, set()):
                # This letter is not at this index in the answer, so this is
                # not a possible guess
                break
        else:
            for letter in hint.misplaced:
                if letter not in word:
                    # This letter exists in the answer, so this is not a
                    # possible guess
                    break
            else:
                filtered_guesses.add(word)

    return filtered_guesses

def score_strings() -> WordScores:
    """Score all possible strings, regardless of whether they are permitted guesses.

    Scores are computed for each character in a string, independently of one
    another. A higher score indicates a better choice of letter.

    Each character's scores are returned in an arbitrary order.
    """
    # Initialize scores to 0
    scores = list(dict.fromkeys(string.ascii_lowercase, 0) for _ in range(words.LENGTH))

    for word in words.possible_words:
        for i in range(words.LENGTH):
            scores[i][word[i]] += 1

    for i in range(words.LENGTH):
        for letter in string.ascii_lowercase:
            # Score each character by its frequency's closeness to 50%. This
            # means the best character is the one that eliminates closest to
            # half the possible words. Note that this is only true per
            # character, so there is correlation between characters that is not
            # considered.
            scores[i][letter] = -abs((len(words.possible_words) // 2) - scores[i][letter])

    return scores

def sort_guesses(guesses: set[str], scores: WordScores) -> list[str]:
    """Sort the given guesses according to the given scores.

    They are returned in nonascending order.
    """
    scored_guesses = {}
    for guess in guesses:
        scored_guesses[guess] = sum(scores[i][guess[i]] for i in range(words.LENGTH))

    sorted_scored_guesses = sorted(scored_guesses.items(), key=lambda item: item[1], reverse=True)
    return [guess for guess, _ in sorted_scored_guesses]

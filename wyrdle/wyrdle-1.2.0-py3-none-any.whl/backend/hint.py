"""A module for administering the information the player receives each round."""

from ..common.hint import Hint

def hint(answer: str, guess: str) -> Hint:
    """Hint at the answer based on a guess."""
    hint = Hint()
    working_answer = answer[:]

    # First, scan for correct letters
    for guess_letter_index, guess_letter in enumerate(guess):
        if working_answer[guess_letter_index] == guess_letter:
            # This letter is correct; register its location
            hint.correct.setdefault(guess_letter, set()).add(guess_letter_index)
            hint.inverse_correct[guess_letter_index] = guess_letter

            # Let's remove this letter from our working answer, so we don't
            # match its specific occurrence again when scanning for misplaced
            # and absent letters.
            #
            # We should replace it with an unmatchable character rather than
            # remove it outright, since we want to preserve the locations of
            # the remaining letters.
            working_answer = working_answer[:guess_letter_index] \
                           + ' ' \
                           + working_answer[guess_letter_index + 1:]

    # Now, scan for misplaced and absent letters
    for guess_letter_index, guess_letter in enumerate(guess):
        if guess_letter_index in hint.inverse_correct:
            # Skip correct letters
            continue

        try:
            answer_letter_index = working_answer.index(guess_letter)
        except ValueError:
            # This letter is absent; register it
            hint.absent.add(guess_letter)
            continue

        # This letter is misplaced; register its location
        hint.misplaced.setdefault(guess_letter, set()).add(guess_letter_index)
        hint.inverse_misplaced.setdefault(guess_letter_index, set()).add(guess_letter)

        # Again, prevent further matches
        working_answer = working_answer[:answer_letter_index] \
                       + ' ' \
                       + working_answer[answer_letter_index + 1:]

    return hint

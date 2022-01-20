# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.tools import is_iterable


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ REMOVE DUPLICATES
# └─────────────────────────────────────────────────────────────────────────────────────


def remove_duplicates(iterable, recursive=False):
    """ Removes duplcates from an iterable while preserving order """

    # Determine type of iterable as a function
    to_type = type(iterable)

    # Initialize seen cache
    seen = set()
    see = seen.add

    # Remove duplicates from iterable
    iterable = [
        remove_duplicates(i, recursive=recursive) if recursive and is_iterable(i) else i
        for i in iterable
        if not (i in seen or see(i))
    ]

    # Return typeified unique iterable
    return to_type(iterable)

"""
description: this module provides function get_or_text.
"""


def get_or_text(items, represent=repr):
    """
    description: this function is used to make a list to
                 string with the conjuctive or.
    """

    if len(items) == 1:
        return represent(items[0])

    return ', '.join([represent(item) for item in items[:-1]]) + ' or ' \
           + represent(items[-1])

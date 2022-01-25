"""
description: this module provides function get_and_text.
"""


def get_and_text(items, represent=repr):
    """
    description: this function is used to
                 make a list to string with the conjuctive and.
    """

    if len(items) == 1:
        return represent(items[0])

    return ', '.join([represent(item) for item in items[:-1]]) + ' and ' \
           + represent(items[-1])

"""Handlers to convert inputs that accept ladybug data collections."""
import json

from ladybug.datacollection import BaseCollection


def value_or_data_to_str(value):
    """Translate a single numerical value or data collection into a string.

    Args:
        value: Either a single numerical value, a data collection.

    Returns:
        str -- string version of the number or JSON array string of data
            collection values.
    """
    if isinstance(value, str):  # ensure the string is of an appropriate type
        try:  # first check to see if it's a valid number
            float(value)
        except ValueError:  # maybe it's a while JSON array of numbers
            loaded_data = json.loads(value)
            assert isinstance(loaded_data, list), \
                'Data string must be either a number or an array.'
    elif isinstance(value, (float, int)):
        value = str(value)
    elif isinstance(value, BaseCollection):
        value = str(list(value.values))
    else:
        raise ValueError(
            'Excpected a single number or a data collection. Not {}.'.format(type(value))
        )
    return value

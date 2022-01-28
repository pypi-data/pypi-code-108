import os

BACKEND_FILE = os.path.join(os.path.dirname(__file__), 'backends.json')


###############################################################################

class BadType(Exception):
    def __init__(self, value, expected_types, not_expected=False):
        if not isinstance(expected_types, (tuple, list)):
            expected_types = [expected_types]
        expected_types = [e.__name__ for e in expected_types]
        if not_expected:
            message = "Did not expected one of those type(s)"
        else:
            message = "Expected one of those type(s)"
        super(BadType, self).__init__("{}: {}, got this value: {}".format(message, expected_types, value))


def CHECK_TYPE(value, expected_types, allow_none=False, exclude_types=None):
    """
    Helper to check that `value` matches `expected_types` (or is None if `allow_none` is True)

    Args:
        value: the instance whose type we must check
        expected_types (type or tuple of types): the allowed types
        allow_none (bool): Allow value to be None
        exclude_types (type or tuple of types): the types to exclude (useful because of sub-typing: isinstance(False, int) == True)

    Return:
        value: unmodified, for ease of use
    """
    if value is None and allow_none:
        return value
    if exclude_types is not None and isinstance(value, exclude_types):
        raise BadType(value, exclude_types, not_expected=True)
    if not isinstance(value, expected_types):
        raise BadType(value, expected_types)
    return value


def CHECK_LIST(value, expected_types):
    """
    Helper to check that `value` is a list and that its values match `expected_types`

    Args:
        value: the instance whose type we must check
        expected_types (type or tuple of types): the allowed types

    Return:
        value: unmodified or replace by an empty container if it was None, for ease of use
    """
    if value is None:
        value = []
    CHECK_TYPE(value, list)
    for x in value:
        CHECK_TYPE(x, expected_types)
    return value


def CHECK_DICT(value, expected_types):
    """
    Helper to check that `value` is a dict and that its values match `expected_types`

    Args:
        value: the instance whose type we must check
        expected_types (type or tuple of types): the allowed types

    Return:
        value: unmodified or replace by an empty container if it was None, for ease of use
    """
    if value is None:
        value = {}
    CHECK_TYPE(value, dict)
    for x in value.values():
        CHECK_TYPE(x, expected_types)
    return value


###############################################################################

def is_true(value):
    return value is True or value == 'true'

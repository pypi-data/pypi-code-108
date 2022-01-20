from configparser import ConfigParser


RAISE_IF_UNKNOWN = object()
NOT_FOUND = object()


__ALL__ = ['parse_boolean', 'parse_strict_boolean', 'DEFAULT_BOOLEAN_STATES', 'STRICT_BOOLEAN_STATES']


STRICT_BOOLEAN_STATES = {
    'TRUE': True,
    'FALSE': False,
}

DEFAULT_BOOLEAN_STATES = ConfigParser.BOOLEAN_STATES


def parse_boolean(obj, boolean_states=DEFAULT_BOOLEAN_STATES, force=False, default=RAISE_IF_UNKNOWN):
    if isinstance(obj, bool):
        return obj

    resp = boolean_states.get(obj.upper() if isinstance(obj, str) else obj, NOT_FOUND)

    if resp is NOT_FOUND:
        resp = bool(obj) if force else default

    if resp is RAISE_IF_UNKNOWN:
        raise TypeError(f"Unable to parse to boolean (boolean_states={boolean_states}, force={force}): {obj!s}")

    return resp


def parse_strict_boolean(obj, default=RAISE_IF_UNKNOWN):
    return parse_boolean(obj, boolean_states=STRICT_BOOLEAN_STATES, default=default)

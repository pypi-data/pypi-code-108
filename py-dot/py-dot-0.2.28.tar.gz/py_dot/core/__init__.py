import re

_NUMERIC = r'([+-])?(\d+(?:\.\d+)?)'


def casting(target):
    """ Auto-casting string as it cast-able

    - bool
        * "true" and "false" for Normal
        * "True" and "False" for `Python`
        * "TRUE" and "FALSE" for `Database`
    - None
        * "null" for Normal
        " "undefined" for `Javascript`
        * "NULL" for `Database`
    - int
        * Number without Decimal Precision Mark
    - float
        * Number with Decimal Precision Mark

    :param target: Cast-able String
    :return: Auto-casted target
    """

    if not isinstance(target, str):
        return target

    if target == 'true' or target == 'True' or target == 'TRUE':
        return True

    if target == 'false' or target == 'False' or target == 'FALSE':
        return False

    if target == 'null' or target == 'NULL' or target == 'undefined':
        return None

    matched = re.fullmatch(_NUMERIC, target)
    if matched:
        if '.' in target:
            return float(target)

        return int(target)

    return target


def to_fixed(value: float, precision: int):
    return float(('%0.' + str(precision) + 'f') % value)

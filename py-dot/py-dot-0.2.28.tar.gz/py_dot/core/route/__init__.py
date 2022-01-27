from typing import Dict, Any

from py_dot.core import casting
from py_dot.core.date import is_period_string, Period, is_digit_timestamp, from_digit_timestamp
from py_dot.core.dicts import to_snake_key

FILTER_KEYWORD_SPACE = '+'
FILTER_KEYWORD_OR = ','


def _get_filter_keyword(
    value: str,
    keyword_space=FILTER_KEYWORD_SPACE,
    keyword_or=FILTER_KEYWORD_OR,
    use_default_timezone=None
):
    or_values = value.split(keyword_or)
    result = []

    for or_value in or_values:
        if len(or_value) == 0:
            continue

        matched_period = is_period_string(or_value)
        if matched_period:
            result.append(Period(matched=matched_period, use_default_timezone=use_default_timezone))
            continue

        matched_digit_timestamp = is_digit_timestamp(or_value)

        if matched_digit_timestamp:
            result.append(from_digit_timestamp(or_value, matched=matched_digit_timestamp))
            continue

        or_value = casting(or_value)
        if isinstance(or_value, str):
            or_value = or_value.replace(keyword_space, ' ')

        result.append(or_value)

    return result if len(result) > 1 else result[0]


def from_query_string(
    query_string: str,
    use_snake_case=False,
    use_default_timezone=False
) -> Dict[str, Any]:
    """ Get Query Condition from Query String

    `foo:bar`:
    >>> {
    ... 'foo': 'bar'
    ...}

    `foo:bar,baz`:
    >>>{
    ...    'foo': ['bar', 'baz']
    ...}


    foo:bar;baz:qux:
    >>>{
    ...    'foo': 'bar',
    ...    'baz': 'qux'
    ...}

    :param query_string: Shortened Search Condition
    :param use_snake_case: Using snake_case to key
    :param use_default_timezone:
    :return:
    """

    conditions = {}
    end = len(query_string)
    stack = ''

    key = ''
    current = 0
    get_column = True

    while current < end:
        char = query_string[current]
        current += 1

        if get_column:
            if char == ':':
                key = stack
                stack = ''
                get_column = False
                continue

        else:
            if char == ';':
                conditions[key] = _get_filter_keyword(stack, use_default_timezone=use_default_timezone)
                stack = ''
                get_column = True
                continue

        stack += char

    if key and stack:
        conditions[key] = _get_filter_keyword(stack, use_default_timezone=use_default_timezone)

    if use_snake_case:
        return to_snake_key(conditions)

    return conditions

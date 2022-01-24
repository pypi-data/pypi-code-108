"""extools.view.criteria
------------------------

Utilities for applying criteria to fields.
"""
import re

EQUAL = 0
NOT_EQUAL = 1
LESS_THAN = 2
LESS_THAN_EQUAL = 3
GREATER_THAN = 4
GREATER_THAN_EQUAL = 5
STARTS_WITH = 6
ENDS_WITH = 7
CONTAINS = 8
REGULAR_EXPRESSION = 9

OPERANDS = (EQUAL, NOT_EQUAL, LESS_THAN, LESS_THAN_EQUAL,
            GREATER_THAN, GREATER_THAN_EQUAL, STARTS_WITH,
            ENDS_WITH, CONTAINS, REGULAR_EXPRESSION, )

def matches_criteria(view, field, operand, value):
    view_value = view.get(field)
    try:
        cast_value = type(view_value)(value)
    except (TypeError, ValueError):
        return False

    if operand == EQUAL:
        return view_value == cast_value
    elif operand == NOT_EQUAL:
        return view_value != cast_value
    elif operand == LESS_THAN:
        return view_value < cast_value
    elif operand == LESS_THAN_EQUAL:
        return view_value <= cast_value
    elif operand == GREATER_THAN:
        return view_value > cast_value
    elif operand == GREATER_THAN_EQUAL:
        return view_value >= cast_value
    elif operand == CONTAINS:
        try:
            return cast_value in view_value
        except:
            return False
    elif operand == STARTS_WITH:
        try:
            return view_value.startswith(cast_value)
        except:
            return False
    elif operand == ENDS_WITH:
        try:
            return view_value.endswith(cast_value)
        except:
            return False
    elif operand == REGULAR_EXPRESSION:
        try:
            return re.search(cast_value, view_value)
        except:
            return False

    return False

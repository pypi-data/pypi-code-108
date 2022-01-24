import re
import typing

from dynamo_io.mock import _tables


class Condition(typing.NamedTuple):

    operation: str
    name_key: str
    comparison: typing.Union[str, typing.List[str]]


def is_query_match(
    row: _tables.Row,
    conditions: typing.List[Condition],
    names: typing.Dict[str, str],
    values: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> bool:
    iterator = (False for c in conditions if not is_match(row, c, names, values))
    return next(iterator, True)


def is_match(
    row: _tables.Row,
    condition: Condition,
    names: typing.Dict[str, str],
    values: typing.Dict[str, typing.Dict[str, typing.Any]],
) -> bool:
    key = names[condition.name_key]

    # With GSI keys, they are sparse and may not exist on all rows. Skip
    # match attempts for rows that do not have the necessary key.
    if key not in row.value:
        return False

    value = row.value[key]["S"]

    if condition.operation == "between":
        lower_value = values[condition.comparison[0]]["S"]
        upper_value = values[condition.comparison[1]]["S"]
        return lower_value <= value <= upper_value

    comparator = typing.cast(str, condition.comparison)
    comparison = values[comparator]["S"]

    if condition.operation == "begins_with":
        return value.startswith(comparison)

    if condition.operation == "=":
        return value == comparison
    elif condition.operation == "<":
        return value < comparison
    elif condition.operation == "<=":
        return value <= comparison
    elif condition.operation == ">":
        return value > comparison
    elif condition.operation == ">=":
        return value >= comparison

    return False


def parse_expression(expression: str) -> typing.List[Condition]:
    if not expression:
        return []

    results = []

    between_rx = re.compile(
        r"(?P<name>[^,\s]+)\s+BETWEEN\s+(?P<a>[^\s,]+)\s+AND\s+(?P<b>[^\s,]+)"
    )
    for name_key, lower_key, upper_key in between_rx.findall(expression):
        results.append(
            Condition(
                operation="between",
                name_key=name_key,
                comparison=[lower_key, upper_key],
            )
        )

    comparison_rx = re.compile(
        r"(?P<name>[^,\s]+)\s*(?P<op>[<>=]+)\s*(?P<value>[^\s,]+)"
    )
    for name_key, operation, value in comparison_rx.findall(expression):
        results.append(
            Condition(
                operation=operation,
                name_key=name_key,
                comparison=value,
            )
        )

    function_rx = re.compile(
        r"(?P<func>[^\s,(]+)"
        + r"\s*\(\s*"
        + r"(?P<name>[^\s,]+)"
        + r"\s*,\s*"
        + r"(?P<value>[^\s]+)\s*\)"
    )
    for function, name_key, value_key in function_rx.findall(expression):
        results.append(
            Condition(
                operation=function,
                name_key=name_key,
                comparison=value_key,
            )
        )

    return results

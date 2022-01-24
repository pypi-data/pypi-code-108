import re
import typing


class Update(typing.NamedTuple):

    action: str
    name_key: str
    value_key: str
    function: str
    secondary_value_key: typing.Optional[str] = None


def get_clause(keyword: str, expression: str) -> typing.Optional[str]:
    if keyword not in expression:
        return None

    start_index = expression.index(keyword) + len(keyword)
    indexes = list(
        sorted(
            [
                expression.find("SET"),
                expression.find("REMOVE"),
                expression.find("ADD"),
                expression.find("DELETE"),
                len(expression),
            ]
        )
    )
    end_index = min([i for i in indexes if i >= start_index])
    return expression[start_index:end_index].strip() or None


def parse_sets(expression: str) -> typing.List[Update]:
    clause = get_clause("SET", expression)
    if not clause:
        return []

    results = []

    assign_rx = re.compile(r"#(?P<name>[^,\s(]+)\s*=\s*:(?P<value>[^\s,(]+)")

    for name_key, value_key in assign_rx.findall(clause):
        results.append(
            Update(
                action="SET",
                name_key=f"#{name_key}",
                value_key=f":{value_key}",
                function="assign",
            )
        )

    function_rx = re.compile(
        r"#(?P<name>[^,\s]+)"
        + r"\s*=\s*if_not_exists\s*\(\s*"
        + r"#(?P<second>[^\s,]+)"
        + r"\s*,\s*"
        + r":(?P<value>[^\s]+)\s*\)"
    )

    for name_key, second_key, value_key in function_rx.findall(clause):
        results.append(
            Update(
                action="SET",
                name_key=f"#{name_key}",
                value_key=f":{value_key}",
                function="if_not_exists",
                secondary_value_key=f"#{second_key}",
            )
        )

    return results


def parse_removes(expression: str) -> typing.List[Update]:
    clause = get_clause("REMOVE", expression)
    if not clause:
        return []

    return [Update("REMOVE", item.strip(), "", "remove") for item in clause.split(",")]


def row_update_from_expression(
    expression: str,
    names: typing.Dict[str, str],
    values: typing.Dict[str, typing.Dict[str, typing.Any]],
    existing_row: dict,
) -> dict:
    out = existing_row.copy()
    for setter in parse_sets(expression):
        name = names[setter.name_key]
        value = values[setter.value_key]
        secondary = names.get(setter.secondary_value_key or "")

        skip_existing = setter.function == "if_not_exists" and existing_row.get(
            secondary
        ) not in (None, "")
        if skip_existing:
            continue

        out[name] = value

    for removal in parse_removes(expression):
        name = names[removal.name_key]
        if name in existing_row:
            del out[name]

    return out

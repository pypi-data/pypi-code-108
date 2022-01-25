from ...utils.join_lines import join_lines


def codable_enum(name: str, raw_type: str | None, items: list[str]) -> str:
    lines = [_codable_enum_first_line(name, raw_type), *items, "}"]
    return join_lines(lines, 1)


def _codable_enum_first_line(name: str, raw_type: str | None) -> str:
    return f"public enum {name}: {'' if raw_type is None else f'{raw_type}, '}Codable {'{'}"


def codable_enum_item(name: str, raw_type: str, value: str) -> str:
    return f"    case {name} = {_wrap_value(value, raw_type)}"


def codable_associated_item(name: str, valtype: str) -> str:
    return f"    case {name}(_ value: {valtype})"


def _wrap_value(value: str, raw_type: str) -> str:
    if raw_type == 'String':
        return '"' + value + '"'
    else:
        return value

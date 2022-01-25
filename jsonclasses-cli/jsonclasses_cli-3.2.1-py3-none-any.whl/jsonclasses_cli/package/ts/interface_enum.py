from ...utils.join_lines import join_lines


def interface_enum(name: str, items: list[str]) -> str:
    lines = [_interface_enum_first_line(name), *items, "}"]
    return join_lines(lines, 1)


def _interface_enum_first_line(name: str) -> str:
    return f"enum {name} {'{'}"


def interface_enum_item(name: str, value: str) -> str:
    return f"    {name} = '{value}',"

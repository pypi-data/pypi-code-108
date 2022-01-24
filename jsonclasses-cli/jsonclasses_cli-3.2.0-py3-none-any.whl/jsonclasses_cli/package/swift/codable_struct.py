from typing import Literal
from ...utils.join_lines import join_lines


def codable_struct(name: str, items: list[str]) -> str:
    lines = [_codable_struct_first_line(name), *items, "}"]
    return join_lines(lines, 1)


def codable_struct_class(name: str, items: list[str]) -> str:
    lines = [_codable_struct_first_line(name, False), *items, "}"]
    return join_lines(lines, 1)


def _codable_struct_first_line(name: str, struct: bool = True) -> str:
    return f"public {'struct' if struct else 'class'} {name}: Codable {'{'}"


def codable_struct_item(access: Literal["public", "fileprivate", "private"],
                        mutability: Literal["let", "var"],
                        name: str,
                        field_type: str,
                        optional: bool,
                        default: str | None = None) -> str:
    return (f"    {access} {mutability} {name}: {field_type}"
            f"{'?' if optional else ''}{f' = {default}' if default else ''}")

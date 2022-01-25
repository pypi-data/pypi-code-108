from typing import Literal
from ...utils.join_lines import join_lines


CodableClassItem = tuple[
    Literal['public', 'private', 'fileprivate'],
    Literal['var', 'let'],
    str,
    str,
    bool
]


def codable_class(name: str, items: list[CodableClassItem], unwrapped: bool = False) -> str:
    return join_lines([
        join_lines([
            _codable_class_first_line(name),
            _codable_class_inst_vars(items, unwrapped),
        ], 1),
        join_lines([
            '    public init(',
            _codable_class_init_param_list(items),
            '    ) {',
            _codable_class_init_assigns(items),
            '    }',
            '}'
        ], 1)
    ], 2)


def _codable_class_first_line(name: str) -> str:
    return f"public class {name}: Codable {'{'}"


def _codable_class_inst_vars(items: list[CodableClassItem], unwrapped: bool) -> str:
    return join_lines(map(lambda i: f"    {i[0]} {i[1]} {i[2]}: {i[3]}{'!' if unwrapped else '?' if i[4] else ''}", items), 1)


def _codable_class_init_param_list(items: list[CodableClassItem]) -> str:
    last = len(items) - 1
    return join_lines(map(lambda i: f"        {i[1][2]}: {i[1][3]}{'? = nil' if i[1][4] else ''}{'' if i[0] == last else ','}", enumerate(items)), 1)


def _codable_class_init_assigns(items: list[CodableClassItem]) -> str:
    return join_lines(map(lambda i: f"        self.{i[2]} = {i[2]}", items), 1)


def codable_class_item(access: Literal["public", "fileprivate", "private"],
                       mutability: Literal["let", "var"],
                       name: str,
                       field_type: str,
                       optional: bool) -> CodableClassItem:
    return (access, mutability, name, field_type, optional)

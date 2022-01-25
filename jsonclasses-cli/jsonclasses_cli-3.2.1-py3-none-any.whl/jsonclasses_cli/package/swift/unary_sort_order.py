from ...utils.join_lines import join_lines

def unary_sort_order(name: str):
    return join_lines([
        _unary_sort_order_first_line(name),
        _unary_sort_if_block(name),
        _unary_sort_order_last_line()
    ])


def _unary_sort_order_first_line(name: str) -> str:
    return f'public prefix func -(rhs: {name}) -> {name} {"{"}'

def _unary_sort_if_block(name: str) -> str:
    return join_lines([
        f'    if rhs.rawValue.starts(with: "-") {"{"}',
        f'        return {name}(rawValue: String(rhs.rawValue.dropFirst()))!',
        f'    {"}"} else {"{"}',
        f'        return {name}(rawValue: "-" + rhs.rawValue)!',
        f'    {"}"}'
    ])

def _unary_sort_order_last_line() -> str:
    return '}'

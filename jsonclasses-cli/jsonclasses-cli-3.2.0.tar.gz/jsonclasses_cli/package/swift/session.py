from .codable_struct import codable_struct, codable_struct_item


def session(items: dict[str, str]) -> str:
    struct_items: list[str] = []
    optional = len(items) != 1
    for (s, c) in items.items():
        struct_item = codable_struct_item('public', 'let', s, c, optional)
        struct_items.append(struct_item)
    return codable_struct('Session', [
        codable_struct_item('public', 'let', 'token', 'String', False),
        *struct_items
    ])

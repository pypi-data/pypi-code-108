from jsonclasses_cli.utils.join_lines import join_lines
from .interface import InterfaceItem, interface, interface_item


def session(items: dict[str, str]) -> str:
    interface_items: list[str] = []
    for (s, c) in items.items():
        name = c + 'Session'
        item = interface_item(s, c, False)
        interface_items.append(_session_interface(name, item))
    return join_lines(interface_items, 2)


def _session_interface(name, item: InterfaceItem) -> str:
    return interface(name, [interface_item('token', 'string', False), item])

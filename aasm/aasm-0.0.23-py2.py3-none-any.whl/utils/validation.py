import keyword
from decimal import Decimal
from typing import List


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_int(value: str) -> bool:
    return value.isdigit() or (value[0] == '-' and value[1:].isdigit())


def is_valid_enum_list(enums: list[str]):
    if not len(enums) or len(enums) % 2:
        return False
    total_sum = Decimal(0.0)
    for enum_pair in zip(*[iter(enums)] * 2):
        if not is_float(enum_pair[1]) or float(enum_pair[1]) < 0.0:
            return False
        total_sum += Decimal(float(enum_pair[1]))
    if total_sum < 99.0 or total_sum > 101.0:
        return False
    return True


def is_valid_name(name: str) -> bool:
    return len(name) and not name[0].isdigit() and (name.isalnum() or "_" in name) and name.lower() not in get_invalid_names()


def get_invalid_names() -> List[str]:
    invalid_names = [ 'send', 'rcv', 'len', 'round', 'list', 'filter', 'self', 'jid',
                      'datetime', 'random', 'numpy', 'json', 'spade', 'copy', 'uuid',
                      'get_json_from_spade_message', 'get_spade_message', 'logger',
                      'BackupBehaviour', 'backup_url', 'backup_period', 'backup_delay' ]
    invalid_names.extend(keyword.kwlist)
    return invalid_names


def print_invalid_names() -> str:
    return ", ".join(get_invalid_names())

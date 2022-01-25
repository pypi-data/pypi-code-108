from typing import Any


def split(item_list: Any, n: int):
    k, m = divmod(len(item_list), n)

    return (item_list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

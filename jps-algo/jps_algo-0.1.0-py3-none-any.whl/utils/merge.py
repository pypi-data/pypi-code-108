from typing import List

from .operation import Operation


def merge(left: List[int], right: List[int], ops: List[Operation]):
    """
    q の値に基づいてソート済みの配列を， q の値に基づいて降順にマージする
    """
    merged = list()
    len_left, len_right = len(left), len(right)
    i, j = 0, 0

    while i < len_left and j < len_right:
        if ops[left[i]].q > ops[right[j]].q:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    if i < len_left:
        merged.extend(left[i:])
    if j < len_right:
        merged.extend(right[j:])
    return merged

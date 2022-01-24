from jsp_exp import Operation
from typing import List


def sort_ops_by(key: str, unsorted_ops: List[Operation]) -> List[Operation]:
    return sorted(unsorted_ops, key=lambda op: getattr(op, key))

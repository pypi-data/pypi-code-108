from upyog.imports import *


__all__ = ["flatten", "uniqueify"]


def flatten(x: Any) -> List[Any]:
    flattened_list = []
    for item in x:
        if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)):
            [flattened_list.append(i) for i in item]
        else:
            flattened_list.append(item)
    return flattened_list


def uniqueify(x: Collection) -> Collection:
    return sorted(list(set(x)))

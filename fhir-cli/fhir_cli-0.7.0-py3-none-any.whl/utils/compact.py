def list_compact(array: list) -> list:
    for index, item in enumerate(array):
        if isinstance(item, dict):
            array[index] = dict_compact(item)
            if not len(array[index]):
                array[index] = None
        elif isinstance(item, list):
            array[index] = list_compact(item)
            if not len(array[index]):
                array[index] = None
    return [item for item in array if item is not None]


def dict_compact(obj: dict) -> dict:
    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = dict_compact(value)
            if not len(obj[key]):
                obj[key] = None
        elif isinstance(value, list):
            obj[key] = list_compact(value)
            if not len(obj[key]):
                obj[key] = None
    return {key: value for key, value in obj.items() if value is not None}

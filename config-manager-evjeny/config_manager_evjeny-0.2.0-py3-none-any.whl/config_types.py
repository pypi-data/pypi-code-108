class BoolType:
    def __new__(cls, value):
        _true_forms = {"true", "yes", "1", "on"}
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in _true_forms
        else:
            return bool(value)


class ListType(list):
    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type

    def __class_getitem__(cls, item_type):
        return cls(item_type)

    @staticmethod
    def empty_split(value: str, sep: str) -> list:
        if value == "":
            return []
        return value.split(sep)

    def _cast_list(self, array: list):
        return [self.item_type(e) for e in array]

    def _cast_string(self, value: str):
        return self._cast_list(array=self.empty_split(value, sep=","))

    def __call__(self, value):
        if isinstance(value, str):
            return self._cast_string(value)
        elif isinstance(value, list):
            return self._cast_list(value)
        else:
            raise Exception(
                f"Can't cast type {type(value)} to list of {self.item_type}"
            )

import click


class MapParamType(click.ParamType):
    name = "map"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            kv_list = value.split(",")
            final_value = dict()
            for kv in kv_list:
                split_kv = kv.split(":")
                final_value[split_kv[0]] = split_kv[1]
            if not isinstance(final_value, dict):
                raise TypeError
            return final_value
        except (ValueError, TypeError, IndexError):
            self.fail(f"{value!r} is not a valid map", param, ctx)


class ListParamType(click.ParamType):
    name = "list"

    def convert(self, value, param, ctx):
        list_value = value.strip(",").split(",")
        return list_value


class FileParamType(click.File):
    name = "file"

    def convert(self, value, param, ctx):
        file = super().convert(value, param, ctx)
        return file.read()


class ChoiceParamType(click.Choice):
    name = "choice"

    def __init__(self, _type, choices):
        self._type = _type
        super(ChoiceParamType, self).__init__(choices=choices)

    def convert(self, value, param, ctx):
        choice = super().convert(value, param, ctx)
        return self._type.convert(choice, param, ctx)


FILE = FileParamType(mode="r", encoding=None, errors="strict", lazy=True, atomic=False)
MAP = MapParamType()
LIST = ListParamType()

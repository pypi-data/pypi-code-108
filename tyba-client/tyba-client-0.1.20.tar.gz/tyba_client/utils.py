from enum import Enum
import typing as t

from marshmallow import fields

T = t.TypeVar('T', bound=Enum)
def string_enum(cls: t.Type[T]) -> t.Type[T]:
    """
    decorator to allow Enums to be used with dataclass_json
    Stolen from:
    https://github.com/lidatong/dataclasses-json/issues/101#issuecomment-506418278""
    """
    class EnumField(fields.Field):
        def _serialize(self, value, attr, obj, **kwargs):
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            return cls[value]
    if (not hasattr(cls, '__metadata__')):
        setattr(cls, '__metadata__', dict())

    metadata = {
        "dataclasses_json": {
            "encoder": lambda v: v.name,
            "decoder": lambda name: cls[name],
            "mm_field": EnumField(),
        }}
    cls.__metadata__.update(metadata)
    return cls


class PVSystFileError(ValueError):
    pass


def read_pvsyst_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        blob = {}
        trace = [blob]
        lines = [line for line in f.readlines() if "=" in line]
        indentations = [len(line) - len(line.lstrip()) for line in lines]
        for indentation, line in zip(indentations, lines):
            if divmod(indentation, 2)[1] != 0:
                raise PVSystFileError(f"invalid indentation at {line}")
        structure = [(y - x) // 2 for x, y in zip(indentations[:-1], indentations[1:])]
        structure.append(0)
        for line, typ in zip(lines, structure):
            stripped = line.strip()
            k, v = stripped.split("=")
            if typ == 0:
                trace[-1][k] = v
            elif typ == 1:
                trace[-1][k] = {"type": v, "items": {}}
                trace.append(trace[-1][k]["items"])
            elif typ < 0:
                trace[-1][k] = v
                for _ in range(-1 * typ):
                    trace.pop()
            else:
                raise PVSystFileError(f"invalid structure at {line}")
    return blob

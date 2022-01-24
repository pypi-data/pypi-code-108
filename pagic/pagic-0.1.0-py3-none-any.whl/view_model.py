import traceback
from typing import Any

from attrs import define


@define
class ViewModel:
    _model: object
    _extra_attrs: dict[str, Any] | None = None
    _wrapped = True

    @classmethod
    def from_many(cls, objects: list) -> list:
        return [cls(obj) for obj in objects]

    def __getattr__(self, key):
        if self._extra_attrs is None:
            try:
                self._extra_attrs = self.extra_attrs()
            except Exception as e:
                traceback.print_exc()
                raise RuntimeError from e

        if key in self._extra_attrs:
            return self._extra_attrs[key]

        value = getattr(self._model, key)
        return value

    def extra_attrs(self):
        return {}

    def _unwrap(self):
        return self._model


def unwrap(obj):
    if hasattr(obj, "_model"):
        return obj._model
    return obj

from __future__ import annotations

from typing import ClassVar, Iterable, TypeVar

import attr

from cloudshell.cp.vcenter.exceptions import BaseVCenterException

PATH_TYPE = TypeVar("PATH_TYPE", bound="VcenterPath")


class VcenterPathEmpty(BaseVCenterException):
    ...


@attr.s(auto_attribs=True)
class VcenterPath:
    SEPARATOR: ClassVar[str] = "/"
    _path: str = ""

    def __attrs_post_init__(self):
        self._path = self._path.replace("\\", "/")

    def __str__(self) -> str:
        return self._path

    def __bool__(self) -> bool:
        return bool(self._path)

    def __add__(self: PATH_TYPE, other: VcenterPath | str) -> PATH_TYPE:
        if not isinstance(other, (VcenterPath, str)):
            raise NotImplementedError
        cls = type(self)
        path = cls(self._path)
        path.append(other)
        return path

    def __iter__(self) -> Iterable[str]:
        return iter(filter(bool, self._path.split(self.SEPARATOR)))

    @property
    def name(self) -> str:
        return self._path.rsplit(self.SEPARATOR, 1)[-1]

    def copy(self: PATH_TYPE) -> PATH_TYPE:
        cls = type(self)
        return cls(self._path)

    def append(self, path: str | VcenterPath):
        path = f"{self._path}{self.SEPARATOR}{str(path)}"
        self._path = path.strip(self.SEPARATOR)

    def pop_head(self) -> str:
        if not self._path:
            raise VcenterPathEmpty

        parts = self._path.split(self.SEPARATOR, 1)
        head = parts[0]
        try:
            path = parts[1]
        except IndexError:
            path = ""
        self._path = path
        return head

    def pop(self) -> str:
        if not self._path:
            raise VcenterPathEmpty

        try:
            path, last = self._path.rsplit(self.SEPARATOR, 1)
        except ValueError:
            path = ""
            last = self.name
        self._path = path
        return last

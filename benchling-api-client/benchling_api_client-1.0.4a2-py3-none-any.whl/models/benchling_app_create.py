from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppCreate")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppCreate:
    """  """

    _name: str
    _description: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("description={}".format(repr(self._description)))
        return "BenchlingAppCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        description = self._description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_description() -> Union[Unset, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, str], UNSET)

        benchling_app_create = cls(
            name=name,
            description=description,
        )

        return benchling_app_create

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def description(self) -> str:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

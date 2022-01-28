from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="InaccessibleResource")


@attr.s(auto_attribs=True, repr=False)
class InaccessibleResource:
    """  """

    _inaccessible_id: Union[Unset, str] = UNSET
    _type: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("inaccessible_id={}".format(repr(self._inaccessible_id)))
        fields.append("type={}".format(repr(self._type)))
        return "InaccessibleResource({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        inaccessible_id = self._inaccessible_id
        type = self._type

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if inaccessible_id is not UNSET:
            field_dict["inaccessibleId"] = inaccessible_id
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_inaccessible_id() -> Union[Unset, str]:
            inaccessible_id = d.pop("inaccessibleId")
            return inaccessible_id

        inaccessible_id = get_inaccessible_id() if "inaccessibleId" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, str]:
            type = d.pop("type")
            return type

        type = get_type() if "type" in d else cast(Union[Unset, str], UNSET)

        inaccessible_resource = cls(
            inaccessible_id=inaccessible_id,
            type=type,
        )

        return inaccessible_resource

    @property
    def inaccessible_id(self) -> str:
        if isinstance(self._inaccessible_id, Unset):
            raise NotPresentError(self, "inaccessible_id")
        return self._inaccessible_id

    @inaccessible_id.setter
    def inaccessible_id(self, value: str) -> None:
        self._inaccessible_id = value

    @inaccessible_id.deleter
    def inaccessible_id(self) -> None:
        self._inaccessible_id = UNSET

    @property
    def type(self) -> str:
        """The type of this inaccessible item. Example values: "custom_entity", "container", "plate", "dna_sequence" """
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

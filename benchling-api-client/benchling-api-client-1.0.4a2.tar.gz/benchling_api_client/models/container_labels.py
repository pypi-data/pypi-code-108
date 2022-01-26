from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerLabels")


@attr.s(auto_attribs=True, repr=False)
class ContainerLabels:
    """  """

    _barcode: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerLabels({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcode = self._barcode
        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if barcode is not UNSET:
            field_dict["barcode"] = barcode
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_barcode() -> Union[Unset, str]:
            barcode = d.pop("barcode")
            return barcode

        barcode = get_barcode() if "barcode" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        container_labels = cls(
            barcode=barcode,
            id=id,
            name=name,
        )

        container_labels.additional_properties = d
        return container_labels

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def barcode(self) -> str:
        if isinstance(self._barcode, Unset):
            raise NotPresentError(self, "barcode")
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        self._barcode = value

    @barcode.deleter
    def barcode(self) -> None:
        self._barcode = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.plate import Plate
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class PlatesPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _plates: Union[Unset, List[Plate]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("plates={}".format(repr(self._plates)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PlatesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        plates: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._plates, Unset):
            plates = []
            for plates_item_data in self._plates:
                plates_item = plates_item_data.to_dict()

                plates.append(plates_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if plates is not UNSET:
            field_dict["plates"] = plates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_plates() -> Union[Unset, List[Plate]]:
            plates = []
            _plates = d.pop("plates")
            for plates_item_data in _plates or []:
                plates_item = Plate.from_dict(plates_item_data)

                plates.append(plates_item)

            return plates

        plates = get_plates() if "plates" in d else cast(Union[Unset, List[Plate]], UNSET)

        plates_paginated_list = cls(
            next_token=next_token,
            plates=plates,
        )

        plates_paginated_list.additional_properties = d
        return plates_paginated_list

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
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

    @property
    def plates(self) -> List[Plate]:
        if isinstance(self._plates, Unset):
            raise NotPresentError(self, "plates")
        return self._plates

    @plates.setter
    def plates(self, value: List[Plate]) -> None:
        self._plates = value

    @plates.deleter
    def plates(self) -> None:
        self._plates = UNSET

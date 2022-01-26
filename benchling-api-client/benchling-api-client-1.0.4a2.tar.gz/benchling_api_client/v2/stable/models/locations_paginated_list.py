from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.location import Location
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class LocationsPaginatedList:
    """  """

    _locations: Union[Unset, List[Location]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("locations={}".format(repr(self._locations)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        locations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._locations, Unset):
            locations = []
            for locations_item_data in self._locations:
                locations_item = locations_item_data.to_dict()

                locations.append(locations_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if locations is not UNSET:
            field_dict["locations"] = locations
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_locations() -> Union[Unset, List[Location]]:
            locations = []
            _locations = d.pop("locations")
            for locations_item_data in _locations or []:
                locations_item = Location.from_dict(locations_item_data)

                locations.append(locations_item)

            return locations

        locations = get_locations() if "locations" in d else cast(Union[Unset, List[Location]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        locations_paginated_list = cls(
            locations=locations,
            next_token=next_token,
        )

        locations_paginated_list.additional_properties = d
        return locations_paginated_list

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
    def locations(self) -> List[Location]:
        if isinstance(self._locations, Unset):
            raise NotPresentError(self, "locations")
        return self._locations

    @locations.setter
    def locations(self, value: List[Location]) -> None:
        self._locations = value

    @locations.deleter
    def locations(self) -> None:
        self._locations = UNSET

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

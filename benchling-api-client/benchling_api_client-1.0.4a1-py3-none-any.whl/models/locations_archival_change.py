from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class LocationsArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of locations along with any IDs of locations, boxes, plates, containers that were archived."""

    _box_ids: Union[Unset, List[str]] = UNSET
    _container_ids: Union[Unset, List[str]] = UNSET
    _location_ids: Union[Unset, List[str]] = UNSET
    _plate_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("box_ids={}".format(repr(self._box_ids)))
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("location_ids={}".format(repr(self._location_ids)))
        fields.append("plate_ids={}".format(repr(self._plate_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        box_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._box_ids, Unset):
            box_ids = self._box_ids

        container_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._container_ids, Unset):
            container_ids = self._container_ids

        location_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._location_ids, Unset):
            location_ids = self._location_ids

        plate_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._plate_ids, Unset):
            plate_ids = self._plate_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if box_ids is not UNSET:
            field_dict["boxIds"] = box_ids
        if container_ids is not UNSET:
            field_dict["containerIds"] = container_ids
        if location_ids is not UNSET:
            field_dict["locationIds"] = location_ids
        if plate_ids is not UNSET:
            field_dict["plateIds"] = plate_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_box_ids() -> Union[Unset, List[str]]:
            box_ids = cast(List[str], d.pop("boxIds"))

            return box_ids

        box_ids = get_box_ids() if "boxIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_container_ids() -> Union[Unset, List[str]]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_location_ids() -> Union[Unset, List[str]]:
            location_ids = cast(List[str], d.pop("locationIds"))

            return location_ids

        location_ids = get_location_ids() if "locationIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_plate_ids() -> Union[Unset, List[str]]:
            plate_ids = cast(List[str], d.pop("plateIds"))

            return plate_ids

        plate_ids = get_plate_ids() if "plateIds" in d else cast(Union[Unset, List[str]], UNSET)

        locations_archival_change = cls(
            box_ids=box_ids,
            container_ids=container_ids,
            location_ids=location_ids,
            plate_ids=plate_ids,
        )

        locations_archival_change.additional_properties = d
        return locations_archival_change

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
    def box_ids(self) -> List[str]:
        if isinstance(self._box_ids, Unset):
            raise NotPresentError(self, "box_ids")
        return self._box_ids

    @box_ids.setter
    def box_ids(self, value: List[str]) -> None:
        self._box_ids = value

    @box_ids.deleter
    def box_ids(self) -> None:
        self._box_ids = UNSET

    @property
    def container_ids(self) -> List[str]:
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @container_ids.deleter
    def container_ids(self) -> None:
        self._container_ids = UNSET

    @property
    def location_ids(self) -> List[str]:
        if isinstance(self._location_ids, Unset):
            raise NotPresentError(self, "location_ids")
        return self._location_ids

    @location_ids.setter
    def location_ids(self, value: List[str]) -> None:
        self._location_ids = value

    @location_ids.deleter
    def location_ids(self) -> None:
        self._location_ids = UNSET

    @property
    def plate_ids(self) -> List[str]:
        if isinstance(self._plate_ids, Unset):
            raise NotPresentError(self, "plate_ids")
        return self._plate_ids

    @plate_ids.setter
    def plate_ids(self, value: List[str]) -> None:
        self._plate_ids = value

    @plate_ids.deleter
    def plate_ids(self) -> None:
        self._plate_ids = UNSET

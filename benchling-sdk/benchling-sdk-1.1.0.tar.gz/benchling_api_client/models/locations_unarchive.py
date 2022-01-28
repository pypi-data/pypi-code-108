from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class LocationsUnarchive:
    """  """

    _location_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("location_ids={}".format(repr(self._location_ids)))
        return "LocationsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        location_ids = self._location_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "locationIds": location_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_location_ids() -> List[str]:
            location_ids = cast(List[str], d.pop("locationIds"))

            return location_ids

        location_ids = get_location_ids() if "locationIds" in d else cast(List[str], UNSET)

        locations_unarchive = cls(
            location_ids=location_ids,
        )

        return locations_unarchive

    @property
    def location_ids(self) -> List[str]:
        """ Array of location IDs """
        if isinstance(self._location_ids, Unset):
            raise NotPresentError(self, "location_ids")
        return self._location_ids

    @location_ids.setter
    def location_ids(self, value: List[str]) -> None:
        self._location_ids = value

from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class PlatesUnarchive:
    """  """

    _plate_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("plate_ids={}".format(repr(self._plate_ids)))
        return "PlatesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        plate_ids = self._plate_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "plateIds": plate_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_plate_ids() -> List[str]:
            plate_ids = cast(List[str], d.pop("plateIds"))

            return plate_ids

        plate_ids = get_plate_ids() if "plateIds" in d else cast(List[str], UNSET)

        plates_unarchive = cls(
            plate_ids=plate_ids,
        )

        return plates_unarchive

    @property
    def plate_ids(self) -> List[str]:
        """ Array of plate IDs """
        if isinstance(self._plate_ids, Unset):
            raise NotPresentError(self, "plate_ids")
        return self._plate_ids

    @plate_ids.setter
    def plate_ids(self, value: List[str]) -> None:
        self._plate_ids = value

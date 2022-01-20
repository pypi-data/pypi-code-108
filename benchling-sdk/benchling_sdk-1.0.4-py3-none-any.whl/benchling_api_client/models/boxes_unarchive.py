from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BoxesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class BoxesUnarchive:
    """  """

    _box_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("box_ids={}".format(repr(self._box_ids)))
        return "BoxesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        box_ids = self._box_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "boxIds": box_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_box_ids() -> List[str]:
            box_ids = cast(List[str], d.pop("boxIds"))

            return box_ids

        box_ids = get_box_ids() if "boxIds" in d else cast(List[str], UNSET)

        boxes_unarchive = cls(
            box_ids=box_ids,
        )

        return boxes_unarchive

    @property
    def box_ids(self) -> List[str]:
        """ Array of box IDs """
        if isinstance(self._box_ids, Unset):
            raise NotPresentError(self, "box_ids")
        return self._box_ids

    @box_ids.setter
    def box_ids(self, value: List[str]) -> None:
        self._box_ids = value

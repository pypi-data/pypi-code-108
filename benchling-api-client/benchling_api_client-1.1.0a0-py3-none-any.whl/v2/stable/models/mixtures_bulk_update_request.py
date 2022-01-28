from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.mixture_bulk_update import MixtureBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixturesBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class MixturesBulkUpdateRequest:
    """  """

    _mixtures: Union[Unset, List[MixtureBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("mixtures={}".format(repr(self._mixtures)))
        return "MixturesBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixtures: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._mixtures, Unset):
            mixtures = []
            for mixtures_item_data in self._mixtures:
                mixtures_item = mixtures_item_data.to_dict()

                mixtures.append(mixtures_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if mixtures is not UNSET:
            field_dict["mixtures"] = mixtures

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_mixtures() -> Union[Unset, List[MixtureBulkUpdate]]:
            mixtures = []
            _mixtures = d.pop("mixtures")
            for mixtures_item_data in _mixtures or []:
                mixtures_item = MixtureBulkUpdate.from_dict(mixtures_item_data)

                mixtures.append(mixtures_item)

            return mixtures

        mixtures = get_mixtures() if "mixtures" in d else cast(Union[Unset, List[MixtureBulkUpdate]], UNSET)

        mixtures_bulk_update_request = cls(
            mixtures=mixtures,
        )

        return mixtures_bulk_update_request

    @property
    def mixtures(self) -> List[MixtureBulkUpdate]:
        if isinstance(self._mixtures, Unset):
            raise NotPresentError(self, "mixtures")
        return self._mixtures

    @mixtures.setter
    def mixtures(self, value: List[MixtureBulkUpdate]) -> None:
        self._mixtures = value

    @mixtures.deleter
    def mixtures(self) -> None:
        self._mixtures = UNSET

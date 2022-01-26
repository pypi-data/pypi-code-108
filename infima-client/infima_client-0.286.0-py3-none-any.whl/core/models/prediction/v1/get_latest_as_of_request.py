from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.core.date import CoreDate
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PredictionV1GetLatestAsOfRequest")


@define(auto_attribs=True)
class PredictionV1GetLatestAsOfRequest:
    """
    Attributes:
        date (Union[Unset, CoreDate]):
    """

    date: Union[Unset, CoreDate] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _date = d.pop("date", UNSET)
        date: Union[Unset, CoreDate]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = CoreDate.from_dict(_date)

        prediction_v1_get_latest_as_of_request = cls(
            date=date,
        )

        prediction_v1_get_latest_as_of_request.additional_properties = d
        return prediction_v1_get_latest_as_of_request

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

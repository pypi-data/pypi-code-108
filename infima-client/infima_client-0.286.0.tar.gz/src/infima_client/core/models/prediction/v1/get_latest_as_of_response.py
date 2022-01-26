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

T = TypeVar("T", bound="PredictionV1GetLatestAsOfResponse")


@define(auto_attribs=True)
class PredictionV1GetLatestAsOfResponse:
    """
    Attributes:
        latest_as_of (Union[Unset, CoreDate]):
    """

    latest_as_of: Union[Unset, CoreDate] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        latest_as_of: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.latest_as_of, Unset):
            latest_as_of = self.latest_as_of.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if latest_as_of is not UNSET:
            field_dict["latestAsOf"] = latest_as_of

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _latest_as_of = d.pop("latestAsOf", UNSET)
        latest_as_of: Union[Unset, CoreDate]
        if isinstance(_latest_as_of, Unset):
            latest_as_of = UNSET
        else:
            latest_as_of = CoreDate.from_dict(_latest_as_of)

        prediction_v1_get_latest_as_of_response = cls(
            latest_as_of=latest_as_of,
        )

        prediction_v1_get_latest_as_of_response.additional_properties = d
        return prediction_v1_get_latest_as_of_response

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

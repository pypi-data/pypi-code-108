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

T = TypeVar("T", bound="PredictionV1GetRequest")


@define(auto_attribs=True)
class PredictionV1GetRequest:
    """
    Attributes:
        symbols (List[str]): Pool CUSIPs or cohort names to fetch individual prepayment predictions. Example: 31417EUD1.
        as_of (Union[Unset, CoreDate]):
    """

    symbols: List[str]
    as_of: Union[Unset, CoreDate] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        symbols = self.symbols

        as_of: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.as_of, Unset):
            as_of = self.as_of.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbols": symbols,
            }
        )
        if as_of is not UNSET:
            field_dict["asOf"] = as_of

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        symbols = cast(List[str], d.pop("symbols"))

        _as_of = d.pop("asOf", UNSET)
        as_of: Union[Unset, CoreDate]
        if isinstance(_as_of, Unset):
            as_of = UNSET
        else:
            as_of = CoreDate.from_dict(_as_of)

        prediction_v1_get_request = cls(
            symbols=symbols,
            as_of=as_of,
        )

        prediction_v1_get_request.additional_properties = d
        return prediction_v1_get_request

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

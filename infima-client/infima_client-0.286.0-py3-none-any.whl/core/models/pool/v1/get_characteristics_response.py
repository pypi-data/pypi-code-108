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

from infima_client.core.models.pool.v1.get_characteristics_response_characteristics import (
    PoolV1GetCharacteristicsResponseCharacteristics,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetCharacteristicsResponse")


@define(auto_attribs=True)
class PoolV1GetCharacteristicsResponse:
    """
    Attributes:
        characteristics (Union[Unset, PoolV1GetCharacteristicsResponseCharacteristics]): Mapping of pool
            characteristics.
    """

    characteristics: Union[
        Unset, PoolV1GetCharacteristicsResponseCharacteristics
    ] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        characteristics: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.characteristics, Unset):
            characteristics = self.characteristics.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if characteristics is not UNSET:
            field_dict["characteristics"] = characteristics

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _characteristics = d.pop("characteristics", UNSET)
        characteristics: Union[Unset, PoolV1GetCharacteristicsResponseCharacteristics]
        if isinstance(_characteristics, Unset):
            characteristics = UNSET
        else:
            characteristics = PoolV1GetCharacteristicsResponseCharacteristics.from_dict(
                _characteristics
            )

        pool_v1_get_characteristics_response = cls(
            characteristics=characteristics,
        )

        pool_v1_get_characteristics_response.additional_properties = d
        return pool_v1_get_characteristics_response

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

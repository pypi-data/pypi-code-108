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

from infima_client.core.models.pool.v1.get_quartiles_response_quartiles import (
    PoolV1GetQuartilesResponseQuartiles,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetQuartilesResponse")


@define(auto_attribs=True)
class PoolV1GetQuartilesResponse:
    """
    Attributes:
        quartiles (Union[Unset, PoolV1GetQuartilesResponseQuartiles]): Mapping of Pool Quartiles.
    """

    quartiles: Union[Unset, PoolV1GetQuartilesResponseQuartiles] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        quartiles: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.quartiles, Unset):
            quartiles = self.quartiles.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if quartiles is not UNSET:
            field_dict["quartiles"] = quartiles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _quartiles = d.pop("quartiles", UNSET)
        quartiles: Union[Unset, PoolV1GetQuartilesResponseQuartiles]
        if isinstance(_quartiles, Unset):
            quartiles = UNSET
        else:
            quartiles = PoolV1GetQuartilesResponseQuartiles.from_dict(_quartiles)

        pool_v1_get_quartiles_response = cls(
            quartiles=quartiles,
        )

        pool_v1_get_quartiles_response.additional_properties = d
        return pool_v1_get_quartiles_response

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

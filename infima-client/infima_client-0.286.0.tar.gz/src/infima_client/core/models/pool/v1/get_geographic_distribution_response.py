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

from infima_client.core.models.pool.v1.get_geographic_distribution_response_geos import (
    PoolV1GetGeographicDistributionResponseGeos,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetGeographicDistributionResponse")


@define(auto_attribs=True)
class PoolV1GetGeographicDistributionResponse:
    """
    Attributes:
        geos (Union[Unset, PoolV1GetGeographicDistributionResponseGeos]): Mapping of pool geographical distributions.
    """

    geos: Union[Unset, PoolV1GetGeographicDistributionResponseGeos] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        geos: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.geos, Unset):
            geos = self.geos.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if geos is not UNSET:
            field_dict["geos"] = geos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _geos = d.pop("geos", UNSET)
        geos: Union[Unset, PoolV1GetGeographicDistributionResponseGeos]
        if isinstance(_geos, Unset):
            geos = UNSET
        else:
            geos = PoolV1GetGeographicDistributionResponseGeos.from_dict(_geos)

        pool_v1_get_geographic_distribution_response = cls(
            geos=geos,
        )

        pool_v1_get_geographic_distribution_response.additional_properties = d
        return pool_v1_get_geographic_distribution_response

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

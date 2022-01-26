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

from infima_client.core.models.pool.v1.get_servicers_response_servicers import (
    PoolV1GetServicersResponseServicers,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetServicersResponse")


@define(auto_attribs=True)
class PoolV1GetServicersResponse:
    """
    Attributes:
        servicers (Union[Unset, PoolV1GetServicersResponseServicers]): Mapping of Pool Servicers.
    """

    servicers: Union[Unset, PoolV1GetServicersResponseServicers] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        servicers: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.servicers, Unset):
            servicers = self.servicers.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if servicers is not UNSET:
            field_dict["servicers"] = servicers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _servicers = d.pop("servicers", UNSET)
        servicers: Union[Unset, PoolV1GetServicersResponseServicers]
        if isinstance(_servicers, Unset):
            servicers = UNSET
        else:
            servicers = PoolV1GetServicersResponseServicers.from_dict(_servicers)

        pool_v1_get_servicers_response = cls(
            servicers=servicers,
        )

        pool_v1_get_servicers_response.additional_properties = d
        return pool_v1_get_servicers_response

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

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

from infima_client.core.models.pool.v1.get_general_distributions_response_distributions import (
    PoolV1GetGeneralDistributionsResponseDistributions,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetGeneralDistributionsResponse")


@define(auto_attribs=True)
class PoolV1GetGeneralDistributionsResponse:
    """
    Attributes:
        distributions (Union[Unset, PoolV1GetGeneralDistributionsResponseDistributions]): Mapping of Pool distributions.
    """

    distributions: Union[
        Unset, PoolV1GetGeneralDistributionsResponseDistributions
    ] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        distributions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.distributions, Unset):
            distributions = self.distributions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if distributions is not UNSET:
            field_dict["distributions"] = distributions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _distributions = d.pop("distributions", UNSET)
        distributions: Union[Unset, PoolV1GetGeneralDistributionsResponseDistributions]
        if isinstance(_distributions, Unset):
            distributions = UNSET
        else:
            distributions = (
                PoolV1GetGeneralDistributionsResponseDistributions.from_dict(
                    _distributions
                )
            )

        pool_v1_get_general_distributions_response = cls(
            distributions=distributions,
        )

        pool_v1_get_general_distributions_response.additional_properties = d
        return pool_v1_get_general_distributions_response

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

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

from infima_client.core.models.search.v0.geo_criterion import SearchV0GeoCriterion
from infima_client.core.models.search.v0.servicer_criterion import (
    SearchV0ServicerCriterion,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0SearchCriterion")


@define(auto_attribs=True)
class SearchV0SearchCriterion:
    """
    Attributes:
        geo (Union[Unset, SearchV0GeoCriterion]):
        servicer (Union[Unset, SearchV0ServicerCriterion]):
    """

    geo: Union[Unset, SearchV0GeoCriterion] = UNSET
    servicer: Union[Unset, SearchV0ServicerCriterion] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        geo: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.geo, Unset):
            geo = self.geo.to_dict()

        servicer: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.servicer, Unset):
            servicer = self.servicer.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if geo is not UNSET:
            field_dict["geo"] = geo
        if servicer is not UNSET:
            field_dict["servicer"] = servicer

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _geo = d.pop("geo", UNSET)
        geo: Union[Unset, SearchV0GeoCriterion]
        if isinstance(_geo, Unset):
            geo = UNSET
        else:
            geo = SearchV0GeoCriterion.from_dict(_geo)

        _servicer = d.pop("servicer", UNSET)
        servicer: Union[Unset, SearchV0ServicerCriterion]
        if isinstance(_servicer, Unset):
            servicer = UNSET
        else:
            servicer = SearchV0ServicerCriterion.from_dict(_servicer)

        search_v0_search_criterion = cls(
            geo=geo,
            servicer=servicer,
        )

        search_v0_search_criterion.additional_properties = d
        return search_v0_search_criterion

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

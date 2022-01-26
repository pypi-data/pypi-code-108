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

from infima_client.core.models.search.v0.attributes_criterion import (
    SearchV0AttributesCriterion,
)
from infima_client.core.models.search.v0.cohort_universe import SearchV0CohortUniverse
from infima_client.core.models.search.v0.prediction_criterion import (
    SearchV0PredictionCriterion,
)
from infima_client.core.models.search.v0.search_criterion import SearchV0SearchCriterion
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0SearchPoolsRequest")


@define(auto_attribs=True)
class SearchV0SearchPoolsRequest:
    """
    Attributes:
        attributes (Union[Unset, SearchV0AttributesCriterion]):
        cohorts (Union[Unset, SearchV0CohortUniverse]):
        criteria (Union[Unset, SearchV0SearchCriterion]):
        predictions (Union[Unset, SearchV0PredictionCriterion]):
    """

    attributes: Union[Unset, SearchV0AttributesCriterion] = UNSET
    cohorts: Union[Unset, SearchV0CohortUniverse] = UNSET
    criteria: Union[Unset, SearchV0SearchCriterion] = UNSET
    predictions: Union[Unset, SearchV0PredictionCriterion] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        cohorts: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cohorts, Unset):
            cohorts = self.cohorts.to_dict()

        criteria: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.criteria, Unset):
            criteria = self.criteria.to_dict()

        predictions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predictions, Unset):
            predictions = self.predictions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if cohorts is not UNSET:
            field_dict["cohorts"] = cohorts
        if criteria is not UNSET:
            field_dict["criteria"] = criteria
        if predictions is not UNSET:
            field_dict["predictions"] = predictions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, SearchV0AttributesCriterion]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = SearchV0AttributesCriterion.from_dict(_attributes)

        _cohorts = d.pop("cohorts", UNSET)
        cohorts: Union[Unset, SearchV0CohortUniverse]
        if isinstance(_cohorts, Unset):
            cohorts = UNSET
        else:
            cohorts = SearchV0CohortUniverse.from_dict(_cohorts)

        _criteria = d.pop("criteria", UNSET)
        criteria: Union[Unset, SearchV0SearchCriterion]
        if isinstance(_criteria, Unset):
            criteria = UNSET
        else:
            criteria = SearchV0SearchCriterion.from_dict(_criteria)

        _predictions = d.pop("predictions", UNSET)
        predictions: Union[Unset, SearchV0PredictionCriterion]
        if isinstance(_predictions, Unset):
            predictions = UNSET
        else:
            predictions = SearchV0PredictionCriterion.from_dict(_predictions)

        search_v0_search_pools_request = cls(
            attributes=attributes,
            cohorts=cohorts,
            criteria=criteria,
            predictions=predictions,
        )

        search_v0_search_pools_request.additional_properties = d
        return search_v0_search_pools_request

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

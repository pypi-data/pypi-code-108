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
)

from attr import define, field

from infima_client.core.models.mbs.cohort_story import MbsCohortStory
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1Cohort")


@define(auto_attribs=True)
class CohortV1Cohort:
    """
    Attributes:
        coupon (Union[Unset, float]):
        name (Union[Unset, str]):
        num_pools (Union[Unset, int]):
        story (Union[Unset, MbsCohortStory]):  Default: MbsCohortStory.NULL_COHORT_STORY.
        ticker (Union[Unset, str]):
        vintage (Union[Unset, int]):
    """

    coupon: Union[Unset, float] = UNSET
    name: Union[Unset, str] = UNSET
    num_pools: Union[Unset, int] = UNSET
    story: Union[Unset, MbsCohortStory] = MbsCohortStory.NULL_COHORT_STORY
    ticker: Union[Unset, str] = UNSET
    vintage: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        coupon = self.coupon
        name = self.name
        num_pools = self.num_pools
        story: Union[Unset, str] = UNSET
        if not isinstance(self.story, Unset):
            story = self.story.value

        ticker = self.ticker
        vintage = self.vintage

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if name is not UNSET:
            field_dict["name"] = name
        if num_pools is not UNSET:
            field_dict["numPools"] = num_pools
        if story is not UNSET:
            field_dict["story"] = story
        if ticker is not UNSET:
            field_dict["ticker"] = ticker
        if vintage is not UNSET:
            field_dict["vintage"] = vintage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        coupon = d.pop("coupon", UNSET)

        name = d.pop("name", UNSET)

        num_pools = d.pop("numPools", UNSET)

        _story = d.pop("story", UNSET)
        story: Union[Unset, MbsCohortStory]
        if isinstance(_story, Unset):
            story = UNSET
        else:
            story = MbsCohortStory(_story)

        ticker = d.pop("ticker", UNSET)

        vintage = d.pop("vintage", UNSET)

        cohort_v1_cohort = cls(
            coupon=coupon,
            name=name,
            num_pools=num_pools,
            story=story,
            ticker=ticker,
            vintage=vintage,
        )

        cohort_v1_cohort.additional_properties = d
        return cohort_v1_cohort

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

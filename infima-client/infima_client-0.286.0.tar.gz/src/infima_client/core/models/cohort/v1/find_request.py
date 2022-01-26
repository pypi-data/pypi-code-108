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

T = TypeVar("T", bound="CohortV1FindRequest")


@define(auto_attribs=True)
class CohortV1FindRequest:
    """
    Attributes:
        coupon (Union[Unset, float]):
        story (Union[Unset, MbsCohortStory]):  Default: MbsCohortStory.NULL_COHORT_STORY.
        ticker (Union[Unset, str]):
        vintage (Union[Unset, int]):
    """

    coupon: Union[Unset, float] = UNSET
    story: Union[Unset, MbsCohortStory] = MbsCohortStory.NULL_COHORT_STORY
    ticker: Union[Unset, str] = UNSET
    vintage: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        coupon = self.coupon
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

        _story = d.pop("story", UNSET)
        story: Union[Unset, MbsCohortStory]
        if isinstance(_story, Unset):
            story = UNSET
        else:
            story = MbsCohortStory(_story)

        ticker = d.pop("ticker", UNSET)

        vintage = d.pop("vintage", UNSET)

        cohort_v1_find_request = cls(
            coupon=coupon,
            story=story,
            ticker=ticker,
            vintage=vintage,
        )

        cohort_v1_find_request.additional_properties = d
        return cohort_v1_find_request

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

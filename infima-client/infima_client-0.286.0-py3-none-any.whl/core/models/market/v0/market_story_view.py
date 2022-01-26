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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="MarketV0MarketStoryView")


@define(auto_attribs=True)
class MarketV0MarketStoryView:
    """
    Attributes:
        coupon (Union[Unset, float]):
        historical (Union[Unset, List[float]]):
        predicted (Union[Unset, List[float]]):
        story (Union[Unset, str]):
        vintage (Union[Unset, int]):
    """

    coupon: Union[Unset, float] = UNSET
    historical: Union[Unset, List[float]] = UNSET
    predicted: Union[Unset, List[float]] = UNSET
    story: Union[Unset, str] = UNSET
    vintage: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        coupon = self.coupon
        historical: Union[Unset, List[float]] = UNSET
        if not isinstance(self.historical, Unset):
            historical = self.historical

        predicted: Union[Unset, List[float]] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

        story = self.story
        vintage = self.vintage

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if historical is not UNSET:
            field_dict["historical"] = historical
        if predicted is not UNSET:
            field_dict["predicted"] = predicted
        if story is not UNSET:
            field_dict["story"] = story
        if vintage is not UNSET:
            field_dict["vintage"] = vintage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        coupon = d.pop("coupon", UNSET)

        historical = cast(List[float], d.pop("historical", UNSET))

        predicted = cast(List[float], d.pop("predicted", UNSET))

        story = d.pop("story", UNSET)

        vintage = d.pop("vintage", UNSET)

        market_v0_market_story_view = cls(
            coupon=coupon,
            historical=historical,
            predicted=predicted,
            story=story,
            vintage=vintage,
        )

        market_v0_market_story_view.additional_properties = d
        return market_v0_market_story_view

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

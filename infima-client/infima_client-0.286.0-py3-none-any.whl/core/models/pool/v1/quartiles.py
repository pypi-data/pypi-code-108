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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1Quartiles")


@define(auto_attribs=True)
class PoolV1Quartiles:
    """Quartile statistics.

    Attributes:
        average (Union[Unset, float]):
        first (Union[Unset, float]):
        maximum (Union[Unset, float]):
        minimum (Union[Unset, float]):
        second (Union[Unset, float]):
        third (Union[Unset, float]):
    """

    average: Union[Unset, float] = UNSET
    first: Union[Unset, float] = UNSET
    maximum: Union[Unset, float] = UNSET
    minimum: Union[Unset, float] = UNSET
    second: Union[Unset, float] = UNSET
    third: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        average = self.average
        first = self.first
        maximum = self.maximum
        minimum = self.minimum
        second = self.second
        third = self.third

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if average is not UNSET:
            field_dict["average"] = average
        if first is not UNSET:
            field_dict["first"] = first
        if maximum is not UNSET:
            field_dict["maximum"] = maximum
        if minimum is not UNSET:
            field_dict["minimum"] = minimum
        if second is not UNSET:
            field_dict["second"] = second
        if third is not UNSET:
            field_dict["third"] = third

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        average = d.pop("average", UNSET)

        first = d.pop("first", UNSET)

        maximum = d.pop("maximum", UNSET)

        minimum = d.pop("minimum", UNSET)

        second = d.pop("second", UNSET)

        third = d.pop("third", UNSET)

        pool_v1_quartiles = cls(
            average=average,
            first=first,
            maximum=maximum,
            minimum=minimum,
            second=second,
            third=third,
        )

        pool_v1_quartiles.additional_properties = d
        return pool_v1_quartiles

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

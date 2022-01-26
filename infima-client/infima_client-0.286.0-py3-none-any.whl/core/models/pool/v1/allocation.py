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

T = TypeVar("T", bound="PoolV1Allocation")


@define(auto_attribs=True)
class PoolV1Allocation:
    """Pool Allocation of Remaining Principal Balance

    Attributes:
        number_loans (Union[Unset, int]): Number of loans remaining.
        percentage_rpb (Union[Unset, float]): Remaining Principal Balance in %
        rpb (Union[Unset, float]): Remaining Principal Balance in $
    """

    number_loans: Union[Unset, int] = UNSET
    percentage_rpb: Union[Unset, float] = UNSET
    rpb: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        number_loans = self.number_loans
        percentage_rpb = self.percentage_rpb
        rpb = self.rpb

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if number_loans is not UNSET:
            field_dict["numberLoans"] = number_loans
        if percentage_rpb is not UNSET:
            field_dict["percentageRpb"] = percentage_rpb
        if rpb is not UNSET:
            field_dict["rpb"] = rpb

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        number_loans = d.pop("numberLoans", UNSET)

        percentage_rpb = d.pop("percentageRpb", UNSET)

        rpb = d.pop("rpb", UNSET)

        pool_v1_allocation = cls(
            number_loans=number_loans,
            percentage_rpb=percentage_rpb,
            rpb=rpb,
        )

        pool_v1_allocation.additional_properties = d
        return pool_v1_allocation

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

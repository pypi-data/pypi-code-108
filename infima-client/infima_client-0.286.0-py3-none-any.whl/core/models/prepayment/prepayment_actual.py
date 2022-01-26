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

from infima_client.core.models.core.factor_date import CoreFactorDate
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PrepaymentPrepaymentActual")


@define(auto_attribs=True)
class PrepaymentPrepaymentActual:
    """
    Attributes:
        cpr (Union[Unset, float]):
        factor_date (Union[Unset, CoreFactorDate]):
        smm (Union[Unset, float]):
    """

    cpr: Union[Unset, float] = UNSET
    factor_date: Union[Unset, CoreFactorDate] = UNSET
    smm: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cpr = self.cpr
        factor_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.factor_date, Unset):
            factor_date = self.factor_date.to_dict()

        smm = self.smm

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cpr is not UNSET:
            field_dict["cpr"] = cpr
        if factor_date is not UNSET:
            field_dict["factorDate"] = factor_date
        if smm is not UNSET:
            field_dict["smm"] = smm

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cpr = d.pop("cpr", UNSET)

        _factor_date = d.pop("factorDate", UNSET)
        factor_date: Union[Unset, CoreFactorDate]
        if isinstance(_factor_date, Unset):
            factor_date = UNSET
        else:
            factor_date = CoreFactorDate.from_dict(_factor_date)

        smm = d.pop("smm", UNSET)

        prepayment_prepayment_actual = cls(
            cpr=cpr,
            factor_date=factor_date,
            smm=smm,
        )

        prepayment_prepayment_actual.additional_properties = d
        return prepayment_prepayment_actual

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

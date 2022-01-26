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

T = TypeVar("T", bound="PoolV1PoolCharacteristics")


@define(auto_attribs=True)
class PoolV1PoolCharacteristics:
    """Pool characteristics: security factor, WAC, WALA, WAM, SMM.

    Attributes:
        cusip (Union[Unset, str]):
        factor (Union[Unset, float]): Pool security factor.
        factor_date (Union[Unset, CoreFactorDate]):
        smm (Union[Unset, float]):
        wac (Union[Unset, float]):
        wala (Union[Unset, int]):
        wam (Union[Unset, int]):
    """

    cusip: Union[Unset, str] = UNSET
    factor: Union[Unset, float] = UNSET
    factor_date: Union[Unset, CoreFactorDate] = UNSET
    smm: Union[Unset, float] = UNSET
    wac: Union[Unset, float] = UNSET
    wala: Union[Unset, int] = UNSET
    wam: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusip = self.cusip
        factor = self.factor
        factor_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.factor_date, Unset):
            factor_date = self.factor_date.to_dict()

        smm = self.smm
        wac = self.wac
        wala = self.wala
        wam = self.wam

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if factor is not UNSET:
            field_dict["factor"] = factor
        if factor_date is not UNSET:
            field_dict["factorDate"] = factor_date
        if smm is not UNSET:
            field_dict["smm"] = smm
        if wac is not UNSET:
            field_dict["wac"] = wac
        if wala is not UNSET:
            field_dict["wala"] = wala
        if wam is not UNSET:
            field_dict["wam"] = wam

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusip = d.pop("cusip", UNSET)

        factor = d.pop("factor", UNSET)

        _factor_date = d.pop("factorDate", UNSET)
        factor_date: Union[Unset, CoreFactorDate]
        if isinstance(_factor_date, Unset):
            factor_date = UNSET
        else:
            factor_date = CoreFactorDate.from_dict(_factor_date)

        smm = d.pop("smm", UNSET)

        wac = d.pop("wac", UNSET)

        wala = d.pop("wala", UNSET)

        wam = d.pop("wam", UNSET)

        pool_v1_pool_characteristics = cls(
            cusip=cusip,
            factor=factor,
            factor_date=factor_date,
            smm=smm,
            wac=wac,
            wala=wala,
            wam=wam,
        )

        pool_v1_pool_characteristics.additional_properties = d
        return pool_v1_pool_characteristics

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

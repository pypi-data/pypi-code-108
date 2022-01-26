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

from infima_client.core.models.pool.v1.quartiles import PoolV1Quartiles
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1PoolQuartileStatistics")


@define(auto_attribs=True)
class PoolV1PoolQuartileStatistics:
    """Quartiles data on loan variables: OCS, OLTV, OLS, Age, ODTI.

    Attributes:
        age (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        coupon (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        cusip (Union[Unset, str]):
        ocltv (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        ocs (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        odti (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        ols (Union[Unset, PoolV1Quartiles]): Quartile statistics.
        oltv (Union[Unset, PoolV1Quartiles]): Quartile statistics.
    """

    age: Union[Unset, PoolV1Quartiles] = UNSET
    coupon: Union[Unset, PoolV1Quartiles] = UNSET
    cusip: Union[Unset, str] = UNSET
    ocltv: Union[Unset, PoolV1Quartiles] = UNSET
    ocs: Union[Unset, PoolV1Quartiles] = UNSET
    odti: Union[Unset, PoolV1Quartiles] = UNSET
    ols: Union[Unset, PoolV1Quartiles] = UNSET
    oltv: Union[Unset, PoolV1Quartiles] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        age: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.age, Unset):
            age = self.age.to_dict()

        coupon: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.coupon, Unset):
            coupon = self.coupon.to_dict()

        cusip = self.cusip
        ocltv: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ocltv, Unset):
            ocltv = self.ocltv.to_dict()

        ocs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ocs, Unset):
            ocs = self.ocs.to_dict()

        odti: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.odti, Unset):
            odti = self.odti.to_dict()

        ols: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ols, Unset):
            ols = self.ols.to_dict()

        oltv: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.oltv, Unset):
            oltv = self.oltv.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if age is not UNSET:
            field_dict["age"] = age
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if ocltv is not UNSET:
            field_dict["ocltv"] = ocltv
        if ocs is not UNSET:
            field_dict["ocs"] = ocs
        if odti is not UNSET:
            field_dict["odti"] = odti
        if ols is not UNSET:
            field_dict["ols"] = ols
        if oltv is not UNSET:
            field_dict["oltv"] = oltv

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _age = d.pop("age", UNSET)
        age: Union[Unset, PoolV1Quartiles]
        if isinstance(_age, Unset):
            age = UNSET
        else:
            age = PoolV1Quartiles.from_dict(_age)

        _coupon = d.pop("coupon", UNSET)
        coupon: Union[Unset, PoolV1Quartiles]
        if isinstance(_coupon, Unset):
            coupon = UNSET
        else:
            coupon = PoolV1Quartiles.from_dict(_coupon)

        cusip = d.pop("cusip", UNSET)

        _ocltv = d.pop("ocltv", UNSET)
        ocltv: Union[Unset, PoolV1Quartiles]
        if isinstance(_ocltv, Unset):
            ocltv = UNSET
        else:
            ocltv = PoolV1Quartiles.from_dict(_ocltv)

        _ocs = d.pop("ocs", UNSET)
        ocs: Union[Unset, PoolV1Quartiles]
        if isinstance(_ocs, Unset):
            ocs = UNSET
        else:
            ocs = PoolV1Quartiles.from_dict(_ocs)

        _odti = d.pop("odti", UNSET)
        odti: Union[Unset, PoolV1Quartiles]
        if isinstance(_odti, Unset):
            odti = UNSET
        else:
            odti = PoolV1Quartiles.from_dict(_odti)

        _ols = d.pop("ols", UNSET)
        ols: Union[Unset, PoolV1Quartiles]
        if isinstance(_ols, Unset):
            ols = UNSET
        else:
            ols = PoolV1Quartiles.from_dict(_ols)

        _oltv = d.pop("oltv", UNSET)
        oltv: Union[Unset, PoolV1Quartiles]
        if isinstance(_oltv, Unset):
            oltv = UNSET
        else:
            oltv = PoolV1Quartiles.from_dict(_oltv)

        pool_v1_pool_quartile_statistics = cls(
            age=age,
            coupon=coupon,
            cusip=cusip,
            ocltv=ocltv,
            ocs=ocs,
            odti=odti,
            ols=ols,
            oltv=oltv,
        )

        pool_v1_pool_quartile_statistics.additional_properties = d
        return pool_v1_pool_quartile_statistics

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

from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.regressor_type import RegressorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="OnDemandPredictForm")


@attr.s(auto_attribs=True)
class OnDemandPredictForm:
    """  """

    horizon: int
    regressor: RegressorType
    filter_target_names: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        horizon = self.horizon
        regressor = self.regressor.value

        filter_target_names = self.filter_target_names

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "horizon": horizon,
                "regressor": regressor,
            }
        )
        if filter_target_names is not UNSET:
            field_dict["filterTargetNames"] = filter_target_names

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        horizon = d.pop("horizon")

        regressor = RegressorType(d.pop("regressor"))

        filter_target_names = d.pop("filterTargetNames", UNSET)

        on_demand_predict_form = cls(
            horizon=horizon,
            regressor=regressor,
            filter_target_names=filter_target_names,
        )

        on_demand_predict_form.additional_properties = d
        return on_demand_predict_form

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

from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProblemSpecificationConfig")


@attr.s(auto_attribs=True)
class ProblemSpecificationConfig:
    """ Properties for a stage  """

    target_features: List[str]
    horizons: List[int]
    data_split: float
    active_columns: List[int]
    scale_factor_multiplier: float
    used_in_lstm: Union[Unset, bool] = UNSET
    type: Union[Unset, str] = "problem_specification"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_features = self.target_features

        horizons = self.horizons

        data_split = self.data_split
        active_columns = self.active_columns

        scale_factor_multiplier = self.scale_factor_multiplier
        used_in_lstm = self.used_in_lstm
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetFeatures": target_features,
                "horizons": horizons,
                "dataSplit": data_split,
                "activeColumns": active_columns,
                "scaleFactorMultiplier": scale_factor_multiplier,
            }
        )
        if used_in_lstm is not UNSET:
            field_dict["usedInLstm"] = used_in_lstm
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_features = cast(List[str], d.pop("targetFeatures"))

        horizons = cast(List[int], d.pop("horizons"))

        data_split = d.pop("dataSplit")

        active_columns = cast(List[int], d.pop("activeColumns"))

        scale_factor_multiplier = d.pop("scaleFactorMultiplier")

        used_in_lstm = d.pop("usedInLstm", UNSET)

        type = d.pop("type", UNSET)

        problem_specification_config = cls(
            target_features=target_features,
            horizons=horizons,
            data_split=data_split,
            active_columns=active_columns,
            scale_factor_multiplier=scale_factor_multiplier,
            used_in_lstm=used_in_lstm,
            type=type,
        )

        problem_specification_config.additional_properties = d
        return problem_specification_config

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

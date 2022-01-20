from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.trading_simulation_options import TradingSimulationOptions
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingSimulationStageConfig")


@attr.s(auto_attribs=True)
class TradingSimulationStageConfig:
    """ Properties for a stage  """

    options: TradingSimulationOptions
    type: Union[Unset, str] = "trading_simulation"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        options = self.options.to_dict()

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "options": options,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        options = TradingSimulationOptions.from_dict(d.pop("options"))

        type = d.pop("type", UNSET)

        trading_simulation_stage_config = cls(
            options=options,
            type=type,
        )

        trading_simulation_stage_config.additional_properties = d
        return trading_simulation_stage_config

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

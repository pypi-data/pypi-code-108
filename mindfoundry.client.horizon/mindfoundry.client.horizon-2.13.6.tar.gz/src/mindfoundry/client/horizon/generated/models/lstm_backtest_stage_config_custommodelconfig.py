from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="LstmBacktestStageConfigCustommodelconfig")


@attr.s(auto_attribs=True)
class LstmBacktestStageConfigCustommodelconfig:
    """ JSON object containing a valid keras.Sequential model configuration, as obtained from calling model.get_config(). It allows users to create their own custom network architecture. If specified, time_steps, number_of_units and dropout are ignored. """

    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        lstm_backtest_stage_config_custommodelconfig = cls()

        lstm_backtest_stage_config_custommodelconfig.additional_properties = d
        return lstm_backtest_stage_config_custommodelconfig

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

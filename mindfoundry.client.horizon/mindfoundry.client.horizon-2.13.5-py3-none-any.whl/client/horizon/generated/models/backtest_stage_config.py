from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.regressor_type import RegressorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BacktestStageConfig")


@attr.s(auto_attribs=True)
class BacktestStageConfig:
    """ Properties for a stage  """

    n_backtests: int
    fold_train_frac: float
    gapping_factor: float
    regressor: RegressorType
    type: Union[Unset, str] = "backtest"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        n_backtests = self.n_backtests
        fold_train_frac = self.fold_train_frac
        gapping_factor = self.gapping_factor
        regressor = self.regressor.value

        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nBacktests": n_backtests,
                "foldTrainFrac": fold_train_frac,
                "gappingFactor": gapping_factor,
                "regressor": regressor,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        n_backtests = d.pop("nBacktests")

        fold_train_frac = d.pop("foldTrainFrac")

        gapping_factor = d.pop("gappingFactor")

        regressor = RegressorType(d.pop("regressor"))

        type = d.pop("type", UNSET)

        backtest_stage_config = cls(
            n_backtests=n_backtests,
            fold_train_frac=fold_train_frac,
            gapping_factor=gapping_factor,
            regressor=regressor,
            type=type,
        )

        backtest_stage_config.additional_properties = d
        return backtest_stage_config

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

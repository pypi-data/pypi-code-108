from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.lstm_backtest_stage_config import LstmBacktestStageConfig
from ..models.stage_status import StageStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="LstmBacktestStage")


@attr.s(auto_attribs=True)
class LstmBacktestStage:
    """A Stage is the key processing block in Horizon. It is a function that is initialised
     with a configuration, and then run with a set of features, outputting a set of
     transformed features and insights.

    Stages must make best effort to be 'composable': wherever possible, they must not
    depend on other stages having been run previously."""

    status: StageStatus
    id: int
    config: LstmBacktestStageConfig
    error_msg: Union[Unset, None, str] = UNSET
    type: Union[Unset, str] = "lstm_backtest"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        id = self.id
        config = self.config.to_dict()

        error_msg = self.error_msg
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "id": id,
                "config": config,
            }
        )
        if error_msg is not UNSET:
            field_dict["errorMsg"] = error_msg
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = StageStatus(d.pop("status"))

        id = d.pop("id")

        config = LstmBacktestStageConfig.from_dict(d.pop("config"))

        error_msg = d.pop("errorMsg", UNSET)

        type = d.pop("type", UNSET)

        lstm_backtest_stage = cls(
            status=status,
            id=id,
            config=config,
            error_msg=error_msg,
            type=type,
        )

        lstm_backtest_stage.additional_properties = d
        return lstm_backtest_stage

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

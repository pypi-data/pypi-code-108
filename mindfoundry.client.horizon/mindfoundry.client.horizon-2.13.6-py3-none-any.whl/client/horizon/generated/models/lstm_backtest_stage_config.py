from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.lstm_backtest_stage_config_custommodelconfig import (
    LstmBacktestStageConfigCustommodelconfig,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LstmBacktestStageConfig")


@attr.s(auto_attribs=True)
class LstmBacktestStageConfig:
    """ Properties for a stage  """

    epochs: int
    type: Union[Unset, str] = "lstm_backtest"
    dropout: Union[Unset, float] = UNSET
    number_of_units: Union[Unset, int] = UNSET
    time_steps: Union[Unset, int] = UNSET
    custom_model_config: Union[Unset, LstmBacktestStageConfigCustommodelconfig] = UNSET
    loss: Union[Unset, str] = UNSET
    optimizer: Union[Unset, str] = UNSET
    learning_rate: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        epochs = self.epochs
        type = self.type
        dropout = self.dropout
        number_of_units = self.number_of_units
        time_steps = self.time_steps
        custom_model_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.custom_model_config, Unset):
            custom_model_config = self.custom_model_config.to_dict()

        loss = self.loss
        optimizer = self.optimizer
        learning_rate = self.learning_rate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "epochs": epochs,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type
        if dropout is not UNSET:
            field_dict["dropout"] = dropout
        if number_of_units is not UNSET:
            field_dict["numberOfUnits"] = number_of_units
        if time_steps is not UNSET:
            field_dict["timeSteps"] = time_steps
        if custom_model_config is not UNSET:
            field_dict["customModelConfig"] = custom_model_config
        if loss is not UNSET:
            field_dict["loss"] = loss
        if optimizer is not UNSET:
            field_dict["optimizer"] = optimizer
        if learning_rate is not UNSET:
            field_dict["learningRate"] = learning_rate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        epochs = d.pop("epochs")

        type = d.pop("type", UNSET)

        dropout = d.pop("dropout", UNSET)

        number_of_units = d.pop("numberOfUnits", UNSET)

        time_steps = d.pop("timeSteps", UNSET)

        _custom_model_config = d.pop("customModelConfig", UNSET)
        custom_model_config: Union[Unset, LstmBacktestStageConfigCustommodelconfig]
        if isinstance(_custom_model_config, Unset):
            custom_model_config = UNSET
        else:
            custom_model_config = LstmBacktestStageConfigCustommodelconfig.from_dict(
                _custom_model_config
            )

        loss = d.pop("loss", UNSET)

        optimizer = d.pop("optimizer", UNSET)

        learning_rate = d.pop("learningRate", UNSET)

        lstm_backtest_stage_config = cls(
            epochs=epochs,
            type=type,
            dropout=dropout,
            number_of_units=number_of_units,
            time_steps=time_steps,
            custom_model_config=custom_model_config,
            loss=loss,
            optimizer=optimizer,
            learning_rate=learning_rate,
        )

        lstm_backtest_stage_config.additional_properties = d
        return lstm_backtest_stage_config

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

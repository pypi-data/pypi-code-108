from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.stage_status import StageStatus
from ..models.trading_algo import TradingAlgo
from ..models.trading_specification_stage_config import TradingSpecificationStageConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingSpecificationStage")


@attr.s(auto_attribs=True)
class TradingSpecificationStage:
    """ Specify basic configuration for a trading pipeline  """

    status: StageStatus
    id: int
    config: TradingSpecificationStageConfig
    error_msg: Union[Unset, None, str] = UNSET
    type: Union[Unset, str] = "trading_specification"
    algo: Union[Unset, TradingAlgo] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        id = self.id
        config = self.config.to_dict()

        error_msg = self.error_msg
        type = self.type
        algo: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.algo, Unset):
            algo = self.algo.to_dict()

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
        if algo is not UNSET:
            field_dict["algo"] = algo

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = StageStatus(d.pop("status"))

        id = d.pop("id")

        config = TradingSpecificationStageConfig.from_dict(d.pop("config"))

        error_msg = d.pop("errorMsg", UNSET)

        type = d.pop("type", UNSET)

        _algo = d.pop("algo", UNSET)
        algo: Union[Unset, TradingAlgo]
        if isinstance(_algo, Unset):
            algo = UNSET
        else:
            algo = TradingAlgo.from_dict(_algo)

        trading_specification_stage = cls(
            status=status,
            id=id,
            config=config,
            error_msg=error_msg,
            type=type,
            algo=algo,
        )

        trading_specification_stage.additional_properties = d
        return trading_specification_stage

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

from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.rebalance_frequency import RebalanceFrequency
from ..models.rebalance_weekly_day import RebalanceWeeklyDay
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingSimulationOptions")


@attr.s(auto_attribs=True)
class TradingSimulationOptions:
    """  """

    targets: Union[Unset, List[str]] = UNSET
    start_timestamp: Union[Unset, None, int] = UNSET
    end_timestamp: Union[Unset, None, int] = UNSET
    starting_capital: Union[Unset, float] = 100000.0
    commission_fraction: Union[Unset, float] = 0.0
    allow_short_positions: Union[Unset, bool] = True
    max_gross_leverage: Union[Unset, float] = 1.0
    rebalance_frequency: Union[Unset, RebalanceFrequency] = RebalanceFrequency.DAILY
    rebalance_weekly_day: Union[Unset, RebalanceWeeklyDay] = RebalanceWeeklyDay.NA
    max_time_in_seconds: Union[Unset, int] = 86400
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        targets: Union[Unset, List[str]] = UNSET
        if not isinstance(self.targets, Unset):
            targets = self.targets

        start_timestamp = self.start_timestamp
        end_timestamp = self.end_timestamp
        starting_capital = self.starting_capital
        commission_fraction = self.commission_fraction
        allow_short_positions = self.allow_short_positions
        max_gross_leverage = self.max_gross_leverage
        rebalance_frequency: Union[Unset, str] = UNSET
        if not isinstance(self.rebalance_frequency, Unset):
            rebalance_frequency = self.rebalance_frequency.value

        rebalance_weekly_day: Union[Unset, str] = UNSET
        if not isinstance(self.rebalance_weekly_day, Unset):
            rebalance_weekly_day = self.rebalance_weekly_day.value

        max_time_in_seconds = self.max_time_in_seconds

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if targets is not UNSET:
            field_dict["targets"] = targets
        if start_timestamp is not UNSET:
            field_dict["startTimestamp"] = start_timestamp
        if end_timestamp is not UNSET:
            field_dict["endTimestamp"] = end_timestamp
        if starting_capital is not UNSET:
            field_dict["startingCapital"] = starting_capital
        if commission_fraction is not UNSET:
            field_dict["commissionFraction"] = commission_fraction
        if allow_short_positions is not UNSET:
            field_dict["allowShortPositions"] = allow_short_positions
        if max_gross_leverage is not UNSET:
            field_dict["maxGrossLeverage"] = max_gross_leverage
        if rebalance_frequency is not UNSET:
            field_dict["rebalanceFrequency"] = rebalance_frequency
        if rebalance_weekly_day is not UNSET:
            field_dict["rebalanceWeeklyDay"] = rebalance_weekly_day
        if max_time_in_seconds is not UNSET:
            field_dict["maxTimeInSeconds"] = max_time_in_seconds

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        targets = cast(List[str], d.pop("targets", UNSET))

        start_timestamp = d.pop("startTimestamp", UNSET)

        end_timestamp = d.pop("endTimestamp", UNSET)

        starting_capital = d.pop("startingCapital", UNSET)

        commission_fraction = d.pop("commissionFraction", UNSET)

        allow_short_positions = d.pop("allowShortPositions", UNSET)

        max_gross_leverage = d.pop("maxGrossLeverage", UNSET)

        _rebalance_frequency = d.pop("rebalanceFrequency", UNSET)
        rebalance_frequency: Union[Unset, RebalanceFrequency]
        if isinstance(_rebalance_frequency, Unset):
            rebalance_frequency = UNSET
        else:
            rebalance_frequency = RebalanceFrequency(_rebalance_frequency)

        _rebalance_weekly_day = d.pop("rebalanceWeeklyDay", UNSET)
        rebalance_weekly_day: Union[Unset, RebalanceWeeklyDay]
        if isinstance(_rebalance_weekly_day, Unset):
            rebalance_weekly_day = UNSET
        else:
            rebalance_weekly_day = RebalanceWeeklyDay(_rebalance_weekly_day)

        max_time_in_seconds = d.pop("maxTimeInSeconds", UNSET)

        trading_simulation_options = cls(
            targets=targets,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            starting_capital=starting_capital,
            commission_fraction=commission_fraction,
            allow_short_positions=allow_short_positions,
            max_gross_leverage=max_gross_leverage,
            rebalance_frequency=rebalance_frequency,
            rebalance_weekly_day=rebalance_weekly_day,
            max_time_in_seconds=max_time_in_seconds,
        )

        trading_simulation_options.additional_properties = d
        return trading_simulation_options

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

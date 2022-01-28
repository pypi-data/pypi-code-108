from datetime import datetime
from typing import List

from mosaik_schedule_flocker.schedule_flocker.core.util import \
    get_schedule_max, get_schedule_min


class ScheduleFlockGeneratorConfig(object):
    """
    Immutable configuration object for the schedule flock generator.
    """

    def __init__(
            self,
            *_,
            start_date: datetime,
            limit_count_activation: int,
            limit_energy_consumption: int,
            limit_energy_production: int,
            limit_power_consumption: int,
            limit_power_production: int,
            limit_size_flock: int,
            predicted_schedule: List,
            predicted_flexibility_potential_positive: List[int],
            predicted_flexibility_potential_negative: List[int],
            limit_time_generation: int,
            unit_type: str,
            unit_id: str
    ):
        # I do not know what to do with the start date
        # So drop it to avoid the linter worrying about it
        del start_date

        # Currently there is no functionality to limit the generation by time
        # So drop it to avoid the linter worrying about it
        del limit_time_generation

        # Derive convenience values from inputs
        self.schedule_max = get_schedule_max(
            predicted_flexibility_potential_positive=
            predicted_flexibility_potential_positive,
            predicted_schedule=predicted_schedule)
        print('schedule_max: %s', self.schedule_max)

        self.schedule_min = get_schedule_min(
            predicted_flexibility_potential_negative=
            predicted_flexibility_potential_negative,
            predicted_schedule=predicted_schedule)
        print('schedule_min: %s', self.schedule_min)

        self._limit_count_activation = limit_count_activation
        self._limit_energy_consumption = limit_energy_consumption
        self._limit_energy_production = limit_energy_production
        self._limit_power_consumption = limit_power_consumption
        self._limit_power_production = limit_power_production
        self._limit_size_flock = limit_size_flock
        self._predicted_schedule = predicted_schedule
        self._predicted_flexibility_potential_positive = \
            predicted_flexibility_potential_positive
        self._predicted_flexibility_potential_negative = \
            predicted_flexibility_potential_negative
        self._unit_type = unit_type
        self._unit_id = unit_id

    @property
    def limit_count_activation(self) -> int:
        return self._limit_count_activation

    @property
    def limit_energy_consumption(self) -> int:
        return self._limit_energy_consumption

    @property
    def limit_energy_production(self) -> int:
        return self._limit_energy_production

    @property
    def limit_power_consumption(self) -> int:
        return self._limit_power_consumption

    @property
    def limit_power_production(self) -> int:
        return self._limit_power_production

    @property
    def limit_size_flock(self) -> int:
        return self._limit_size_flock

    @property
    def predicted_schedule(self) -> List:
        return self._predicted_schedule

    @property
    def unit_id(self) -> str:
        return self._unit_id

    @property
    def unit_type(self) -> str:
        return self._unit_type

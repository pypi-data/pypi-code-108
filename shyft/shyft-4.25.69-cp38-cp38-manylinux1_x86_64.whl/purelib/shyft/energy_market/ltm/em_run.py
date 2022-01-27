"""
EMRun represents a consistent simulation, and contains a model
with various results within a unique namespace defined by the run id.
"""
import json
from typing import Any
from shyft.energy_market import core
from shyft.time_series import Calendar, deltahours, TimeAxis


class EMRun(core.Run):
    def __init__(self, id: int, name: str, info: str):
        super().__init__(id, name, info)
        self.model = None
        self.calendar = Calendar()

        self.fine_time_axis = None
        self.coarse_time_axis = None
        self.wv_time_axis = None
        self.time_axis = None
        self.front_price_time_axis = None

        self._water_value_repository_construct = None
        self._dispatch_center_repository = None

        self.make_time_axes()

    @property
    def run(self) -> "EMRun":
        return self

    @property
    def tag(self) -> str:
        return f"R{self.id}"

    def set_model(self, model) -> None:
        """
        Assign a model to the run.
        Moreover sets run as parent to model.
        :param model: (dm.ModelBase) Model to assign to run.
        """
        self.model = model
        self.model.parent = self

    @classmethod
    def extend_from_core_run(cls, run: core.Run,
                             calendar: Calendar = Calendar(),
                             water_value_repository_construct=None,
                             dispatch_center_repository=None) -> "EMRun":
        if not isinstance(run, core.Run):
            raise RuntimeError(f'extend from core run: type of run must be core.Run, was {type(run)}')
        run.__class__ = cls
        run.calendar = calendar
        run._water_value_repository_construct = water_value_repository_construct
        run._dispatch_center_repository = dispatch_center_repository
        run.make_time_axes()
        return run

    @classmethod
    def create_start(cls, calendar: Calendar, year: int, week: int, weekday: int = 1):
        return calendar.time_from_week(year, week, weekday, 0, 0, 0)

    def make_time_axes(self) -> None:
        """
        Offloaded initialization.
        """
        info = json.loads(self.json)
        start_week = info["start_week"]
        start_year = info["start_year"]

        calendar = self.calendar
        start = self.create_start(calendar, start_year, start_week)
        f_start = self.create_start(calendar, start_year, start_week, info["start_day_of_week"])
        week_dt = calendar.WEEK
        day_dt = calendar.DAY
        fine_dt = deltahours(
            24*7//info["num_periods_per_week"])  # TimeSpan(0, 0, 24 * 7 / num_periods_per_week * 3600)
        num_simulated_weeks = info["end_week"] - start_week + 1
        # Find how many week 53s we have
        weeks = [calendar.calendar_week_units(calendar.add(start, calendar.WEEK, i)) for i in
                 range(num_simulated_weeks)]
        total_extra_weeks = weeks.count(53)
        n = ((num_simulated_weeks + total_extra_weeks)*week_dt - (info["start_day_of_week"] - 1)*day_dt)//fine_dt
        self.fine_time_axis = TimeAxis(f_start, fine_dt, n)
        self.coarse_time_axis = TimeAxis(start, week_dt, num_simulated_weeks + total_extra_weeks)
        #  Below, the code related to wv_start is due to lack of data from Sintef, we
        #  try to fix this using the run-created date. To be removed
        #  and replaced by the 'real' water-value reference date once available from sintef

        wv_start = max(start, Calendar('Europe/Oslo').trim(self.created,
                                                           calendar.DAY))  # max safeguard, and water value for local time oslo day
        self.wv_time_axis = TimeAxis(wv_start, calendar.HOUR, 1)
        self.time_axis = self.coarse_time_axis
        if info["front_price_dt"]:
            self.front_price_time_axis = TimeAxis(info["front_price_t0"], info["front_price_dt"],
                                                  info["front_price_n"])
        else:
            self.front_price_time_axis = None

    def collect_area_tss(self, ts_collector: Any) -> Any:
        """
        Entry point for collecting area time series.
        """
        return self.model.collect_area_tss(ts_collector)

    def collect_detailed_tss(self, ts_collector: Any) -> Any:
        """
        Entry point for collecting detailed hydro time series.
        """
        return self.model.collect_detailed_tss(ts_collector)

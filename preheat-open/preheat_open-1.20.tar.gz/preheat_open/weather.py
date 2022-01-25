import pandas as pd
from pandas import DataFrame

from .component import Component
from .data import load_weather_data
from .helpers import now, sanitise_datetime_input, timedelta
from .unit import Unit


class Weather(Unit):
    """Weather; an extension of Unit to handle Weather extraction"""

    def __init__(self, location_id, weather_data):
        super().__init__("weather", weather_data)
        self.location_id = location_id
        self.id = weather_data.pop("gridId", None)
        self.name = "WeatherForecast"

        for type_i in weather_data["types"]:
            self.components.append(Component(type_i))

    def load_data(
        self, start_date, end_date, time_resolution="hour", components=None
    ) -> None:
        # Parse strings to datetime object
        start_date = sanitise_datetime_input(start_date)
        end_date = sanitise_datetime_input(end_date)

        self._warn_if_data_is_loaded()
        components_to_load = self.get_all_component_ids(components=components)
        if components is not None:
            components_to_load = {
                k: components_to_load[k]
                for k in components_to_load
                if components_to_load[k] in components
            }

        if (end_date - start_date) > pd.Timedelta("180d"):
            # Batch in 6M intervals (max we can load at a time)
            parts = list(pd.date_range(start_date, end_date, freq="2Q"))

            if start_date != parts[0]:
                parts.insert(0, start_date)
            if end_date != parts[-1]:
                parts.append(end_date)

            parts[0] -= pd.Timedelta("1d")  # we add back one day later

            pairs = zip(map(lambda d: d + pd.Timedelta("1d"), parts[:-1]), parts[1:])

            dfs = []
            for start_date, end_date in pairs:
                dfs.append(
                    load_weather_data(
                        self.location_id,
                        components_to_load,
                        start_date,
                        end_date,
                        time_resolution,
                    )
                )

            res = pd.concat(dfs)

        else:
            res = load_weather_data(
                self.location_id,
                components_to_load,
                start_date,
                end_date,
                time_resolution,
            )

        self.data = res  # type: DataFrame
        self._ensure_continuity_of_data(time_resolution)

    def load_state(self, seconds_back: int = 3600, t_now=None) -> None:
        t_now = now() if t_now is None else sanitise_datetime_input(t_now)

        components_to_load = self.get_all_component_ids()
        self._state = load_weather_data(
            self.location_id,
            components_to_load,
            t_now - timedelta(seconds=seconds_back),
            t_now,
            "hour",
        )

    def get_state(
        self,
        update: bool = False,
        estimate: str = "last",
        seconds_back: int = 3600,
        **kwargs
    ) -> pd.Series:
        return super().get_state(
            update=update, estimate=estimate, seconds_back=seconds_back, **kwargs
        )

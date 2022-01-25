"""Forecast module provides methods to generate forecasts with fake data.

Methods in this module return pd.Dataframes with the same format than client
methods.

Examples
--------
>>> from datetime import datetime, timezone as tz
>>> from bambooapi_client.testing import api_client_mock
>>> from bambooapi_client.testing.factory.models import SiteDataPointFactory
>>> sites_api_mock = api_client_mock().sites_api()
>>> forecast_df = timeseries_factory_from_datapoints([
...     SiteDataPointFactory(
...         time=datetime(2021, 5, 1, tzinfo=tz.utc),
...         power=15.0,
...         temperature=25.0,
...     ),
...     SiteDataPointFactory(
...         time=datetime(2021, 5, 2, tzinfo=tz.utc),
...         power=10.0,
...         temperature=20.0,
...      ),
... ])
>>> sites_api_mock.read_device_baseline_forecasts.return_value = forecast_df
"""

from typing import List, Type, Union

from bambooapi_client.model.site_data_point import SiteDataPoint
from bambooapi_client.model.weather_data_point import WeatherDataPoint
from bambooapi_client.testing.factory.models import Factory

import pandas as pd


def timeseries_factory_from_datapoints(
    datapoints: List[Union[SiteDataPoint, WeatherDataPoint]],
) -> pd.DataFrame:
    """Create a forecast dataframe from a list of datapoints.

    Notes
    -----
    The return type matches SiteApi methods that return a dataframe of
    SiteDataPoints.

    Examples
    --------
    >>> from bambooapi_client.testing.factory.models import SiteDataPointFactory
    >>> from datetime import datetime, timezone as tz
    >>> forecast_df = timeseries_factory_from_datapoints([
    ...     SiteDataPointFactory(
    ...         time=datetime(2021, 5, 1, tzinfo=tz.utc),
    ...         power=15.0,
    ...         temperature=25.0,
    ...     ),
    ...     SiteDataPointFactory(
    ...         time=datetime(2021, 5, 2, tzinfo=tz.utc),
    ...         power=10.0,
    ...         temperature=20.0,
    ...      ),
    ... ])
    >>> sorted(list(forecast_df.columns))
    ['availability', 'humidity', 'mode', 'power', 'powersp', 'quality', 'schedule', 'soc', 'status', 'temperature', 'tempsp', 'vref']
    >>> forecast_df.index.name
    'time'
    >>> forecast_df['power']
    time
    2021-05-01 00:00:00+00:00    15.0
    2021-05-02 00:00:00+00:00    10.0
    Name: power, dtype: float64
    >>> forecast_df['temperature']
    time
    2021-05-01 00:00:00+00:00    25.0
    2021-05-02 00:00:00+00:00    20.0
    Name: temperature, dtype: float64

    See Also
    --------
    timeseries_factory_from_dataframe
    """  # noqa: E501
    df = pd.DataFrame([dp.to_dict() for dp in datapoints])
    df = df.set_index('time')
    return df


def timeseries_factory_from_dataframe(
    df: pd.DataFrame,
    *,
    factory_class: Type[Factory],
) -> pd.DataFrame:
    """Create a forecast dataframe from a pd.DataFrame.

    Notes
    -----
    The return type matches SiteApi methods that return a dataframe of
    SiteDataPoints.

    Examples
    --------
    >>> import pandas as pd
    >>> from datetime import datetime, timezone as tz
    >>> from bambooapi_client.testing.factory.models import SiteDataPointFactory
    >>> df = pd.DataFrame(
    ...     [[15.0, 25.0], [10.0, 20.0]],
    ...     index=[
    ...         datetime(2021, 5, 1, tzinfo=tz.utc),
    ...         datetime(2021, 5, 2, tzinfo=tz.utc),
    ...     ],
    ...     columns=['power', 'temperature'],
    ... )
    >>> forecast_df = timeseries_factory_from_dataframe(
    ...     df,
    ...     factory_class=SiteDataPointFactory,
    ... )
    >>> sorted(list(forecast_df.columns))
    ['availability', 'humidity', 'mode', 'power', 'powersp', 'quality', 'schedule', 'soc', 'status', 'temperature', 'tempsp', 'vref']
    >>> forecast_df.index.name
    'time'
    >>> forecast_df['power']
    time
    2021-05-01 00:00:00+00:00    15.0
    2021-05-02 00:00:00+00:00    10.0
    Name: power, dtype: float64
    >>> forecast_df['temperature']
    time
    2021-05-01 00:00:00+00:00    25.0
    2021-05-02 00:00:00+00:00    20.0
    Name: temperature, dtype: float64

    See Also
    --------
    timeseries_factory_from_datapoints
    """  # noqa: E501
    model_class = factory_class.model
    if (
        hasattr(model_class, 'attribute_map') and isinstance(model_class, dict)
    ):
        df = df.filter(model_class.attribute_map.keys(), axis=1)

    datapoints = [
        factory_class(**{
            **dict(zip(tup._fields[1:], tup[1:])),
            'time': tup[0].to_pydatetime(),
        })
        for tup in df.itertuples()
    ]
    return timeseries_factory_from_datapoints(datapoints)

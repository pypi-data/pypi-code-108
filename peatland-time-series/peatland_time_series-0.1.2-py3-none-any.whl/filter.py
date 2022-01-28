from typing import Optional

import pandas


def filter_sy(
        sy: pandas.DataFrame,
        sy_min: Optional[float] = None,
        sy_max: Optional[float] = None,
        precipitation_sum_min: Optional[float] = None,
        precipitation_sum_max: Optional[float] = None,
        depth_min: Optional[float] = None,
        depth_max: Optional[float] = None,
        delta_h_min: Optional[float] = None,
        delta_h_max: Optional[float] = None,
        date_beginning_min: Optional[pandas.Timestamp] = None,
        date_beginning_max: Optional[pandas.Timestamp] = None,
        date_ending_min: Optional[pandas.Timestamp] = None,
        date_ending_max: Optional[pandas.Timestamp] = None,
        intesities_min: Optional[float] = None,
        intesities_max: Optional[float] = None) -> pandas.DataFrame:
    """Filter the Specific Yield (Sy).

    Parameters
    ----------
    sy
        The specific yield dataframe, which has the format
        outputed by the calculated_sy function.
    sy_min
    sy_max
    precipitation_sum_min
    precipitation_sum_max
    depth_min
    depth_max
    delta_h_min
    delta_h_max
    date_beginning_min
    date_beginning_max
    date_ending_min
    date_ending_max
    intesities_min
    intesities_max

    Returns
    -------
    pandas.DataFrame
        The Filtered Specific Yield (Sy).
    """
    return _filter_sy(
        sy,
        sy_min=sy_min,
        sy_max=sy_max,
        precipitation_sum_min=precipitation_sum_min,
        precipitation_sum_max=precipitation_sum_max,
        depth_min=depth_min,
        depth_max=depth_max,
        delta_h_min=delta_h_min,
        delta_h_max=delta_h_max,
        date_beginning_min=date_beginning_min,
        date_beginning_max=date_beginning_max,
        date_ending_min=date_ending_min,
        date_ending_max=date_ending_max,
        intesities_min=intesities_min,
        intesities_max=intesities_max
    )


def _filter_sy(sy: pandas.DataFrame, **kwargs) -> pandas.DataFrame:
    for key, value in kwargs.items():
        if value:
            key, min_or_max = key.rsplit('_', 1)  # Only split on the last occurence

            if min_or_max == 'min':
                sy = sy[sy[key] > value]

            elif min_or_max == 'max':
                sy = sy[sy[key] < value]

    return sy

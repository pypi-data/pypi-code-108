from typing import Union

import numpy as np
import pandas
import pandas as pd

SY_DATAFRAME_COLUMNS = ['date_beginning', 'date_ending', 'precipitation_sum', 'max_wtd', 'min_wtd',
                        'durations', 'intensities', 'delta_h', 'depth', 'sy', 'idx_max', 'idx_min',
                        'accuracy_mean', 'accuracy_std']


def calculate_sy(
        time_series: pd.DataFrame,
        gap: int = 5,
        max_hour: int = 5,
        threshold: float = 0.3,
        resample: Union[pandas.DateOffset, pandas.Timedelta, str] = 'H') -> pd.DataFrame:
    """Calculate the Specific Yield (Sy) from given time series.

    Parameters
    ----------
    time_series : pandas.Dataframe
        DataFrame of time series gotten from the `read_time_series` function.
         The DataFrame have at least the  following columns: 'date', 'data_wtd' and 'data_prec'.
        'date' refers to the date of the data acquisition ("YYYY-MM-DD hh:mm:ss", ex. "2011-06-15 15:00:00").
        'data_wtd' refers to the water table depth to the surface.
        'data_prec' refers to the precipitation measure.
    gap : int
        Time which makes it possible to isolate rainy events.
        For example, if it does not rain for 6 hours and the gap parameter is equal to 5,
        the precipitation will be separated into two rainy events.
    max_hour : int
        Parameter that limits the search for the maximum in the water level after a precipitation.
    threshold : float
        Precision threshold.
    resample : str
        Resample rule for the aggregation step. See pandas.DataFrame.resample doc for more details.

    Returns
    -------
    pandas.DataFrame
        Profile of effectives porosity.
    """
    ####### DEFINE_DATA ########
    time = time_series.index.astype('datetime64[ns]')  # the index is the 'date' column
    water_table_depth = time_series['data_wtd']
    precipitation = time_series['data_prec']

    ####### TRANSFORM_IN_PANDAS_DATAFRAME #######
    df_water_table_depth = pd.DataFrame(water_table_depth)
    df_water_table_depth.index = time

    df_precipitation = pd.DataFrame(precipitation)
    df_precipitation.index = time

    ####### RESAMPLE DATA #########
    df_water_table_depth = df_water_table_depth.resample(resample).mean()
    df_precipitation = df_precipitation.resample(resample).sum()

    ####### FIND PRECIPITATION EVENTS #########
    position60 = np.array(np.where(df_precipitation.data_prec.values > threshold)).squeeze()
    diff60 = np.diff(position60)
    gap60 = np.array(np.where(diff60 >= gap)).squeeze()
    gap61 = np.insert(gap60, 0, -1)
    gap61 = gap61[:-1]

    ####### ISOLATION_PRECIPITATION_EVENT ######
    list_event = list()
    precipitation_sum = np.zeros(len(gap61))
    for j in range(0, len(gap61)):
        precipitation_event = position60[gap61[j] + 1:gap60[j] + 1]
        list_event.append(precipitation_event)

        precipitation_sum[j] = df_precipitation.iloc[precipitation_event].sum().values

    ####### BEGIN_END_NB_EVENTS #######
    beginning = position60[gap61 + 1]
    end = position60[gap60]
    dates_beginning = df_precipitation.iloc[position60[gap61 + 1]].index
    dates_ending = df_precipitation.iloc[position60[gap60]].index

    ######## CREATE_MATRIX_FOR_MIN_MAX_IDENTIFICATION ########
    water_table_depths = list()
    idx_max = list()
    idx_min = list()

    for i in range(0, len(beginning)):
        water_table_depths.append(df_water_table_depth.iloc[beginning[i]:end[i] + max_hour].values.squeeze())
        idx_max.append(df_water_table_depth.iloc[beginning[i]:end[i] + max_hour].idxmax().tolist()[0])
        idx_min.append(df_water_table_depth.iloc[beginning[i]:end[i] + max_hour].idxmin().tolist()[0])

    ######## CALCULATE MIN_MAX_WTD ########
    max_wtd = np.array([i.max() for i in water_table_depths])
    min_wtd = np.array([i.min() for i in water_table_depths])

    ######## ACCURACY CALCULATION ########
    wtd_list_it_all = []
    for j in range(5, 15):
        wtd_list_it = list()

        for i in range(0, len(beginning)):
            wtd_list_it.append(df_water_table_depth.iloc[beginning[i]:end[i] + j].values.squeeze())

        max_wtd_it = [i.max() for i in wtd_list_it]
        wtd_list_it_all.append(max_wtd_it)

    accuracy_means = pd.DataFrame(wtd_list_it_all).diff(axis=0).mean(axis=0).values
    accuracy_stds = pd.DataFrame(wtd_list_it_all).diff(axis=0).std(axis=0).values

    ######## SY_CALCULATION_AND_PREC_INTENSITY ########
    # Added to account for rapid precipitation
    durations = []
    for date_beginning, date_ending in zip(dates_beginning, dates_ending):
        if (date_ending - date_beginning).seconds == 0:
            durations.append(0.5)
        else:
            durations.append((date_ending - date_beginning).seconds // 3600)

    durations_array = np.array(durations)
    intensities = precipitation_sum / durations_array
    delta_h = max_wtd - min_wtd
    sy = (precipitation_sum / delta_h) / 1000
    depth = (max_wtd + min_wtd) / 2

    ######## CREATE SUMMARY TABLE ########
    summary_table = pd.DataFrame({
        'date_beginning': dates_beginning,
        'date_ending': dates_ending,
        'precipitation_sum': precipitation_sum,
        'max_wtd': max_wtd,
        'min_wtd': min_wtd,
        'durations': durations,
        'intensities': intensities,
        'delta_h': delta_h,
        'depth': depth,
        'sy': sy,
        'idx_max': idx_max,
        'idx_min': idx_min,
        'accuracy_mean': accuracy_means,
        'accuracy_std': accuracy_stds
    })

    return summary_table


def read_sy(filepath: str) -> pandas.DataFrame:
    """Read the Sy file as a DataFrame.

    Read the Sy csv file which was precedently calculated with
    the `calculate_sy` function and saved as sy_df.to_csv(...).

    Parameters
    ----------
    filepath
        CSV like file of Sy (see the `calculate_sy` for more information
        on the format).

    Returns
    -------
    pandas.DataFrame
        DataFrame of the Sy with related infromation.
    """
    sy = pandas.read_csv(filepath)

    for column in SY_DATAFRAME_COLUMNS:
        if column not in sy.columns:
            raise ValueError(f"Columns \"{', '.join(SY_DATAFRAME_COLUMNS)}\" must be in the Sy file: \"{filepath}\"")

    # Dates are of string type, they have to be converted to datetime to be usable.
    sy['date_beginning'] = pandas.to_datetime(sy['date_beginning'])
    sy['date_ending'] = pandas.to_datetime(sy['date_ending'])

    sy['idx_min'] = pandas.to_datetime(sy['idx_min'])
    sy['idx_max'] = pandas.to_datetime(sy['idx_max'])

    return sy

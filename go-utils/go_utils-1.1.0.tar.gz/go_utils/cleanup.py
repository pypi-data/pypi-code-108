import logging

import numpy as np
import pandas as pd
from pytz import timezone
from timezonefinder import TimezoneFinder

__doc__ = """

# Overview
This submodule contains several methods to assist with data cleanup.
The following sections discuss some of the decisions behind these methods and their part of a larger data cleanup pipeline.

# Methods

## Remove Redundant/Homogenous Column:
[This method](#remove_homogenous_cols) indentifies and removes columns where all values were the same. If the logging level is set to INFO, the method will also print the names of the dropped columns and their respective singular value as a Python dictionary. 
For the raw mosquito habitat mapper data, the following were dropped: 
- {'protocol': 'mosquito_habitat_mapper'} 
- {'ExtraData': None} 
- {'MosquitoEggCount': None} 
- {'DataSource': 'GLOBE Observer App'}

For raw landcover data, the following were dropped:
- {'protocol': 'land_covers'}

## Rename columns:

### Differentiating between MGRS and GPS Columns: 
The GLOBE API data for `MosquitoHabitatMapper` and `LandCovers` report each observation’s Military Grid Reference System (MGRS) Coordinates in the `latitude` and `longitude` fields. The GPS Coordinates are stored in the `MeasurementLatitude` and `MeasurementLongitude` fields. 
To avoid confusion between these measuring systems, [this method](#rename_latlon_cols) renames `latitude` and `longitude` to `MGRSLatitude` and `MGRSLongitude`, respectively, and `MeasurementLatitude` and `MeasurementLongitude` to `Latitude` and `Longitude`, respectively. Now, the official `Latitude` and `Longitude` columns are more intuitively named.

### Protocol Abbreviation:
To better support future cross-protocol analysis and data enrichment, [this method](#replace_column_prefix) following naming scheme for all column names: `protocolAbbreviation_columnName`, where `protocolAbbreviation` was the abbreviation for the protocol (`mhm` for mosquito habitat mapper and `lc` for land cover) and `columnName` was the original name of the column. For example, the mosquito habitat mapper “MGRSLongitude” column was renamed “mhm_MGRSLongitude” and the corresponding land cover column was renamed “lc_MGRSLongitude”.

Do note that if you would like to use the previously mentioned `mhm` and `lc` naming scheme for you data, the `go_utils.mhm` and `go_utils.lc` submodules each have a method called `cleanup_column_prefix` which uses the previously mentioned naming scheme as opposed to the `replace_column_prefix` method which requires that you specify the current prefix and desired prefix.

## Standardize no-data values:
The GLOBE API CSV’s lacked standardization in indicating No Data. Indicators ranged from Python's `None`, to `“null”`, to an empty cell, to `NaN` (`np.nan`). To improve the computational efficiency in future mathematical algorithms on the GLOBE datasets, [this method](#standardize_null_values) converts all No Data Indicators to np.nan (Python NumPy’s version of No-Data as a float). Do note that later in Round Appropriate Columns, all numerical extraneous values are converted from np.nan to -9999.  Thus, Users will receive the pre-processed GLOBE API Mosquito Habitat Mapper and Land Cover Data in accordance with the standards described by Cook et al (2018). 

## Round Appropriate Columns
[This method](#round_cols) does the following:
1. Identifies all numerical columns (e.g. `float64`, `float`, `int`, `int64`).
2. Rounds Latitudes and Longitude Columns to 5 places. To reduce data density, all latitude and longitude values were rounded to 5 decimal places. This corresponds to about a meter of accuracy. Furthermore, any larger number of decimal places consume unnecessary amounts of storage as the GLOBE Observer app cannot attain such precision.
3. Converts other Numerical Data to Integers. To improve the datasets’ memory and performance, non latitude and longitude numerical values were converted to integers for the remaining columns, including `Id`, `MeasurementElevation`, and `elevation` columns.  This is appropriate since ids are always discrete values. `MeasurementElevation` and `elevation` are imprecise estimates from 3rd party sources, rendering additional precision an unnecessary waste of memory. However, by converting these values to integers, we could no longer use np.nan, a float, to denote extraneous/empty values. Thus, for integer columns, we used -9999 to denote extraneous/empty values.

**Note**: Larvae Counts were also converted to integers and Land Classification Column percentages were also converted to integers, reducing our data density. This logic is further discussed in go_utils.mhm.larvae_to_num for mosquito habitat mapper and go_utils.lc.unpack_classifications

"""


def adjust_timezones(df, time_col, latitude_col, longitude_col, inplace=False):
    """
    Calculates timezone offset and adjusts date columns accordingly. This is done because GLOBE data uses UTC timezones and it can be useful to have the time adjusted to the local observation time.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to adjust time zones for
    time_col : str
        The column that contains the time zone data
    latitude_col : str
        The column that contains latitude data
    longitude_col : str
        The column that contains longitude data
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with its time entry adjusted to its local timezone. If `inplace=True` it returns None.
    """
    tf = TimezoneFinder()

    def convert_timezone(time, latitude, longitude):
        utc_tz = pd.to_datetime(time, utc=True)
        local_time_zone = timezone(tf.timezone_at(lng=longitude, lat=latitude))
        return utc_tz.astimezone(local_time_zone)

    time_zone_converter = np.vectorize(convert_timezone)

    if not inplace:
        df = df.copy()

    df[time_col] = time_zone_converter(
        df[time_col].to_numpy(),
        df[latitude_col].to_numpy(),
        df[longitude_col].to_numpy(),
    )

    if not inplace:
        return df


def filter_invalid_coords(
    df, latitude_col, longitude_col, inclusive=False, inplace=False
):
    """
    Filters latitude and longitude of a DataFrame to lie within the latitude range of [-90, 90] or (-90, 90) and longitude range of [-180, 180] or (-180, 180)

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter
    latitude_col : str
        The name of the column that contains latitude values
    longitude_col : str
        The name of the column that contains longitude values
    inclusive : bool, default=False
        True if you would like the bounds of the latitude and longitude to be inclusive e.g. [-90, 90]. Do note that these bounds may not work with certain GIS software and projections.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with invalid latitude and longitude entries removed. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()

    if inclusive:
        mask = (
            (df[latitude_col] >= -90)
            & (df[latitude_col] <= 90)
            & (df[longitude_col] <= 180)
            & (df[longitude_col] >= -180)
        )
    else:
        mask = (
            (df[latitude_col] > -90)
            & (df[latitude_col] < 90)
            & (df[longitude_col] < 180)
            & (df[longitude_col] > -180)
        )

    if not inplace:
        return df[mask]
    else:
        df.mask(~mask, inplace=True)
        df.dropna(inplace=True)


def remove_homogenous_cols(df, exclude=[], inplace=False):
    """
    Removes columns froma DataFrame if they contain only 1 unique value.
    ```

    Then the original `df` variable that was passed is now updated with these dropped columns.

    If you would like to see the columns that are dropped, setting the logging level to info will allow for that to happen.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame that will be modified
    exclude : list of str, default=[]
        A list of any columns that should be excluded from this removal.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with homogenous columns removed. If `inplace=True` it returns None.
    """

    if not inplace:
        df = df.copy()

    for column in df.columns:
        try:
            if column not in exclude and len(pd.unique(df[column])) == 1:
                logging.info(f"Dropped: {df[column].iloc[0]}")
                df.drop(column, axis=1, inplace=True)
        except TypeError:
            continue

    if not inplace:
        return df


def replace_column_prefix(df, current_prefix, replacement_text, inplace=False):
    """
    Replaces the protocol prefix (e.g. mosquito_habitat_mapper/mosquitohabitatmapper) for the column names with another prefix in the format of `newPrefix_columnName`.

    If you are interested in replacing the prefixes for the raw mosquito habitat mapper and landcover datasets, use the go_utils.lc.cleanup_column_prefix and go_utils.mhm.cleanup_column_prefix methods.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame you would like updated
    protocol : str
        A string representing the protocol prefix.
    replacement_text : str
        A string representing the desired prefix for the column name.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the column prefixes replaced. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()
    df.columns = [
        f"{replacement_text}_{column.replace(current_prefix,'')}"
        for column in df.columns
    ]
    if not inplace:
        return df


def find_column(df, keyword):
    """Finds the first column that contains a certain keyword. Mainly intended to be a utility function for some of the other methods.


    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the columns that need to be searched.
    keyword: str
        The keyword that needs to be present in the desired column.
    """

    return [column for column in df.columns if keyword in column][0]


def camel_case(string, delimiters=[" "]):
    """Converts a string into camel case

    Parameters
    ----------
    string: str, the string to convert
    delimiter: str, the character that denotes separate words
    """
    for delimiter in delimiters:
        str_list = [s[0].upper() + s[1:] for s in string.split(delimiter)]
        string = "".join([s for s in str_list])
    return string


def rename_latlon_cols(
    df,
    gps_latitude="",
    gps_longitude="",
    mgrs_latitude="latitude",
    mgrs_longitude="longitude",
    inplace=False,
):
    """Renames the latitude and longitude columns of **raw** GLOBE Observer Data to make the naming intuitive.

    [This](#differentiating-between-mgrs-and-gps-columns) explains the motivation behind the method.

    Example usage:
    ```python
    from go_utils.cleanup import rename_latlon_cols
    rename_latlon_cols(df)
    ```

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame whose columns require renaming.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the updated Latitude and Longitude column names. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()

    if not gps_latitude:
        gps_latitude = find_column(df, "MeasurementLatitude")
    if not gps_longitude:
        gps_longitude = find_column(df, "MeasurementLongitude")
    df.rename(
        {
            gps_latitude: "Latitude",
            gps_longitude: "Longitude",
            mgrs_latitude: "MGRSLatitude",
            mgrs_longitude: "MGRSLongitude",
        },
        axis=1,
        inplace=True,
    )

    if not inplace:
        return df


def round_cols(df, inplace=False):
    """This rounds columns in the DataFrame. More specifically, latitude and longitude data is rounded to 5 decimal places, other fields are rounded to integers, and null values (for the integer columns) are set to -9999.

    See [here](#round-appropriate-columns) for more information.

    Example usage:
    ```python
    from go_utils.cleanup import round_cols
    round_cols(df)
    ```

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame that requires rounding.
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the rounded values. If `inplace=True` it returns None.
    """
    if not inplace:
        df = df.copy()
    # Identifies all the numerical cols
    number_cols = [
        df.columns[i]
        for i in range(len(df.dtypes))
        if (df.dtypes[i] == "float64")
        or (df.dtypes[i] == "float")
        or (df.dtypes[i] == "int")
        or (df.dtypes[i] == "int64")
    ]

    # Rounds cols appropriately
    column_round = np.vectorize(lambda x, digits: round(x, digits))
    for name in number_cols:
        df[name] = df[name].fillna(-9999)
        if ("latitude" in name.lower()) or ("longitude" in name.lower()):
            logging.info(f"Rounded to 5 decimals: {name}")
            df[name] = column_round(df[name].to_numpy(), 5)
        else:
            logging.info(f"Converted to integer: {name}")
            df[name] = df[name].to_numpy().astype(int)

    if not inplace:
        return df


def standardize_null_vals(df, null_val=np.nan, inplace=False):
    """
    This method standardizes the null values of **raw** GLOBE Observer Data.

    ```python
    from go_utils.cleanup import standardize_null_vals
    standardize_null_vals(df)
    ```

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame that needs null value standardization
    null_val : obj, default=np.nan
        The value that all null values should be set to
    inplace : bool, default=False
        Whether to return a new DataFrame. If True then no DataFrame copy is not returned and the operation is performed in place.

    Returns
    -------
    pd.DataFrame or None
        A DataFrame with the standardized null values. If `inplace=True` it returns None.
    """

    if not inplace:
        df = df.copy()

    # Replace Null Values with null_val
    df.fillna(null_val, inplace=True)

    # Replace any text null values
    df.replace(
        {
            "null": null_val,
            "": null_val,
            "NaN": null_val,
            "nan": null_val,
            None: null_val,
        },
        inplace=True,
    )

    if not inplace:
        return df

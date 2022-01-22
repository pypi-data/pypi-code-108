# Imports
from typing import Optional, List, Union, Tuple

from . import _credentials
from . import endpoints

import pandas as pd
from datetime import datetime

# All
__all__ = [
    "get_data_list",
    "get_time_values",
    "get_batch_types_list",
    "get_batch_type_details",
    "get_batch_values",
]


# Pandas DataFrames
def get_data_list(
    query: Optional[str] = None,
    types: Optional[List[str]] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
    get_full_list: bool = False,
    expand_measurement: bool = True,
    expand_tags: bool = True,
) -> pd.DataFrame:
    """
    Gather the list of existing data into a Pandas DataFrame.
    Results are paginated (by default 20 elements per page), but setting 'get_full_list' at True will loop over pages
    and get all data.

    Parameters
    ----------
    query: str, optional
        The text to search for specific data
    types: str or List[str], optional
        A type or a list of types of data to consider
    page: int, optional
        The number of the page to retrieve (API returns the first page by default)
    size: int, optional
        Size of a page (API uses 20 by default)
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.
    get_full_list: bool, default False
        Whether or not the full list should be retrieved by iterating over pages
    expand_measurement: bool, default True
        Whether or not the measurements should be expanded into multiples DataFrame columns
    expand_tags: bool, default True
        Whether or not the tags should be expanded into multiples DataFrame columns

    Returns
    -------
    A DataFrame containing the list of data matching the query
    """

    # Queries
    if get_full_list is False:
        response = endpoints.query_data_list(
            query=query,
            types=types,
            page=page,
            size=size,
            api_credentials=api_credentials,
        )
        if response.status_code != 200:
            raise endpoints.QueryError(
                f"Error {response.status_code}: {response.json()['error']}"
            )
        content = response.json()["content"]
    else:
        content = []
        page = 0
        data_list_complete = False
        while data_list_complete is False:
            response = endpoints.query_data_list(
                query=query, types=types, page=page, api_credentials=api_credentials
            )
            if response.status_code != 200:
                raise endpoints.QueryError(
                    f"Error {response.status_code}: {response.json()['error']}"
                )
            content.extend(response.json()["content"])
            if len(content) == response.json()["totalElements"]:
                data_list_complete = True
            page += 1

    # Convert to DataFrame
    content_df = pd.DataFrame(content)

    # Reformat tags
    content_df["tags"] = content_df["tags"].map(
        lambda tags: {tag["key"]: tag["value"] for tag in tags}
    )

    # Split DataFrame
    df = content_df[["id", "reference", "description", "dataType"]].copy()
    measurement = content_df["measurement"].copy()
    tags = content_df["tags"].copy()

    # Rejoin DataFrame
    if expand_measurement is False:
        df["measurement"] = measurement
    else:
        df = df.join(
            measurement.apply(pd.Series).rename(columns={"name": "measurement"})
        )

    if expand_tags is False:
        df["tags"] = tags
    else:
        df = df.join(tags.apply(pd.Series))

    # Output
    return df


def get_time_values(
    data_reference: Union[str, List[str]],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    aggregation_period: Optional[str] = None,
    aggregation_function: Optional[str] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> pd.DataFrame:
    """
    Gather time values into a single Pandas DataFrame.

    Parameters
    ----------
    data_reference: str or List[str]
        Data references to be retrieved
    start_date: str or datetime
        The beginning of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T14:42:00.000Z'
    end_date: str or datetime
        The end of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T16:42:00.000Z'
    aggregation: str
        How to aggregate values. Possible values are 'TIME', 'GLOBAL' or 'RAW_VALUES'.
    aggregation_period: str
        The sampling period in case of a 'TIME' aggregation. Should be in ISO 8601 format, e.g. 'PT8H'
    aggregation_function: str
        The aggregation function to be used in case of a 'TIME' aggregation. Possible values are 'FIRST', 'LAST',
        'LAST_MINUS_FIRST', 'SUM', 'MIN', 'MAX', 'MEAN', 'MEDIAN', 'STDEV', 'PERCENTILE5', 'PERCENTILE95', 'DECILE1',
        'DECILE9', 'QUARTILE1', 'QUARTILE9', 'COUNT', 'MEAN_MINUS_SIGMA', 'MEAN_PLUS_SIGMA', 'MEAN_MINUS_TWO_SIGMA',
        'MEAN_PLUS_TWO_SIGMA', 'MEAN_MINUS_THREE_SIGMA', 'MEAN_PLUS_THREE_SIGMA', 'VALUE_CHANGE'
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.

    Returns
    -------
    A single DataFrame containing all the specified time values (each data is a column).
    """

    # Query
    response = endpoints.query_time_values(
        data_reference=data_reference,
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        api_credentials=api_credentials,
    )
    if response.status_code != 200:
        raise endpoints.QueryError(
            f"Error {response.status_code}: {response.json()['error']}"
        )

    # Convert to DataFrame
    df = pd.DataFrame()

    for data in response.json():
        ts: pd.DataFrame = pd.DataFrame(data["values"])
        ts["timestamp"] = pd.to_datetime(ts["timestamp"])
        ts.rename(columns={"value": data["dataReference"]}, inplace=True)
        ts.set_index("timestamp", inplace=True)

        df = df.join(ts, how="outer")

    # Output
    return df


def get_batch_types_list(
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
    get_full_list: bool = False,
) -> pd.DataFrame:
    """
    Gather the list of existing batch types into a Pandas DataFrame.

    Parameters
    ----------
    page: int, optional
        The number of the page to retrieve (API returns the first page by default)
    size: int, optional
        Size of a page (API uses 20 by default)
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.
    get_full_list: bool, default False
        Whether or not the full list should be retrieved by iterating over pages

    Returns
    -------
    A DataFrame containing all the existing batch types.
    """

    # Queries
    if get_full_list is False:
        response = endpoints.query_batch_types_list(
            page=page, size=size, api_credentials=api_credentials
        )
        if response.status_code != 200:
            raise endpoints.QueryError(
                f"Error {response.status_code}: {response.json()['error']}"
            )
        content = response.json()["content"]
    else:
        content = []
        page = 0
        batch_types_list_complete = False
        while batch_types_list_complete is False:
            response = endpoints.query_batch_types_list(
                page=page, api_credentials=api_credentials
            )
            if response.status_code != 200:
                raise endpoints.QueryError(
                    f"Error {response.status_code}: {response.json()['error']}"
                )
            content.extend(response.json()["content"])
            if len(content) == response.json()["totalElements"]:
                batch_types_list_complete = True
            page += 1

    # Convert to DataFrame
    content_df = pd.DataFrame(content).set_index("id")

    # Output
    return content_df


def get_batch_type_details(
    batch_type_id: str,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Get the details about a certain batch type. Returns multiple DataFrames corresponding to different types of
    information.

    Parameters
    ----------
    batch_type_id: str
        The ID of the batch type to be retrieved
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.

    Returns
    -------
    Returns multiple DataFrames, in order:
        - Steps definition (ID, name and localisation)
        - List of features associated to the batch type (ID and key)
    """

    # Query
    response = endpoints.query_batch_type_details(
        batch_type_id=batch_type_id,
        api_credentials=api_credentials,
    )
    if response.status_code != 200:
        raise endpoints.QueryError(
            f"Error {response.status_code}: {response.json()['error']}"
        )

    # Convert to DataFrames
    steps = response.json()["steps"]
    features = response.json()["features"]

    if len(steps) > 0:
        batch_steps = pd.DataFrame(steps).set_index("id")
    else:
        batch_steps = None

    if len(features) > 0:
        batch_features = pd.DataFrame(features).set_index("id")
    else:
        batch_features = None

    # Output
    return batch_steps, batch_features


def get_batch_values(
    batch_type_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    name: Optional[str] = None,
    tag_values: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Gather a list of batches, their steps, values and features into multiple DataFrames.

    Parameters
    ----------
    batch_type_id: str
        The ID of the batch type to be retrieved
    start_date: str or datetime
        The beginning of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T14:42:00.000Z'
    end_date: str or datetime
        The end of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T16:42:00.000Z'
    name: str, optional
        A string that should be contained by all batch names returned
    tag_values: str or List[str], optional
        Possibly multiple tag value ids each returned batch should match
    page: int, optional
        The number of the page to retrieve (API returns the first page by default)
    size: int, optional
        Size of a page (API uses 20 by default)
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.

    Returns
    -------
    Returns multiple DataFrames, in order:
        - Steps (with dates) of the retrieved batches
        - Values and features of the retrieved batches (each data or feature is a column)
    """

    # Query
    response = endpoints.query_batch_values(
        batch_type_id=batch_type_id,
        start_date=start_date,
        end_date=end_date,
        name=name,
        tag_values=tag_values,
        page=page,
        size=size,
        api_credentials=api_credentials,
    )
    if response.status_code != 200:
        raise endpoints.QueryError(
            f"Error {response.status_code}: {response.json()['error']}"
        )

    # Convert to DataFrames
    df_steps = pd.DataFrame()
    df_values = pd.DataFrame()

    for batch in response.json()["content"]:
        # Steps
        batch_steps = batch["steps"]
        if len(batch_steps) > 0:
            df_steps_batch = pd.DataFrame(batch_steps)
            df_steps_batch["batch_id"] = batch["id"]
            df_steps_batch["batch_name"] = batch["name"]
            df_steps_batch["batch_timestamp"] = batch["timestamp"]

            # Reorder and expand
            df_steps_batch = (
                df_steps_batch[["batch_id", "batch_name", "batch_timestamp"]]
                .join(df_steps_batch["step"].apply(pd.Series).add_prefix("step_"))
                .join(df_steps_batch[["start", "end", "localisation"]])
            )

            # Append
            df_steps = df_steps.append(df_steps_batch, ignore_index=True)

        # Values and features
        dict_batch = {"batch": batch["name"], "timestamp": batch["timestamp"]}
        if len(batch["values"]) > 0:
            dict_batch_values = {
                value["data"]["reference"]: value["value"] for value in batch["values"]
            }
            dict_batch = dict(dict_batch, **dict_batch_values)
        if len(batch["features"]) > 0:
            dict_batch_features = {
                feature["tagKey"]["key"]: feature["value"]
                for feature in batch["features"]
            }
            dict_batch = dict(dict_batch, **dict_batch_features)

        df_values = df_values.append(pd.DataFrame(dict_batch, index=[batch["id"]]))

    # Convert to datetimes
    if df_steps.shape[0] == 0:
        return None, None
    else:
        df_steps["batch_timestamp"] = pd.to_datetime(df_steps["batch_timestamp"])
        df_steps["start"] = pd.to_datetime(df_steps["start"])
        df_steps["end"] = pd.to_datetime(df_steps["end"])
        df_values["timestamp"] = pd.to_datetime(df_values["timestamp"])

    # Outputs
    return df_steps, df_values


def upload_time_series(
    data: Union[pd.Series, pd.DataFrame],
    units: Union[str, dict],
    api_credentials: Optional[_credentials.OIAnalyticsAPICredentials] = None,
):
    """
    Upload time series to OIAnalytics

    Parameters
    ----------
    data: pd.Series or pd.DataFrame
        Data to upload. Can be a single Series or a whole DataFrame. The index must be a DatetimeIndex.
    units: str or dict
        Can be a single str if data is a Series, or should be a dict in the form of {dataReference: unit, ...}
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.

    Returns
    -------
    Endpoint response
    """

    # Build DTO
    body = []

    if isinstance(data, pd.Series):
        units = {data.name: units}
        data = pd.DataFrame(data)
    else:
        data = data.copy()

    for col in data.columns:
        ser = data[col]
        ser.index = ser.index.tz_localize(None).rename("timestamp").map(lambda x: f"{x.isoformat()}")
        ser.name = "value"
        body.append(
            {
                "dataReference": col,
                "unit": units[col],
                "values": pd.DataFrame(ser).reset_index().to_dict(orient="records"),
            }
        )

    # Query endpoint
    response = endpoints.insert_time_values(body, api_credentials=api_credentials)

    # Output
    return response

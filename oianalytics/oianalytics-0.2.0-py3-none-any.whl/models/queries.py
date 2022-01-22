from typing import Union, List, Optional
from datetime import datetime

from oianalytics import api

from ._dtos import ModelExecutionDTO
from . import utils

CURRENT_EVENT: Optional[ModelExecutionDTO] = None


def set_current_event(event: ModelExecutionDTO):
    """
    Put an execution event into a global variable, for external use

    Parameters
    ----------
    event: ModelExecutionDTO
    """

    global CURRENT_EVENT
    CURRENT_EVENT = event


def get_current_event():
    global CURRENT_EVENT
    return CURRENT_EVENT


def retrieve_time_values(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    data_list: Optional[Union[str, List[str]]] = None,
    time_input_dict: Optional[dict] = None,
    aggregation_period: Optional[str] = None,
    aggregation_function: Optional[str] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    """
    Retrieve time values into a DataFrame, renaming data in order to be used in a model not knowing the actual
    data references.
    It can be called using a minimal set of arguments, automatically using the current event information.

    Parameters
    ----------
    start_date: str or datetime
        The beginning of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T14:42:00.000Z'
    end_date: str or datetime
        The end of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T16:42:00.000Z'
    aggregation: str
        How to aggregate values. Possible values are 'TIME', 'GLOBAL' or 'RAW_VALUES'.
    data_list: str or List[str], optional
        The data aliases to query, can be a str in case of a single data, a list of str in case of multiples data.
        If None, it is automatically built gathering time data references in the current event.
    time_input_dict: dict, optional
        A dictionary referencing OIAnalytics data references, in the form of {data_alias: data_reference, ...}
        If None, it is automatically built gathering time data references in the current event.
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
    A DataFrame containing all joined time values
    """

    global CURRENT_EVENT
    if time_input_dict is None:
        time_input_dict = CURRENT_EVENT.pythonModelInstance.get_input_dict(
            input_types=["STORED_CONTINUOUS_DATA", "COMPUTED_CONTINUOUS_DATA"]
        )

    if isinstance(data_list, str):
        data_list = [data_list]
    elif data_list is None:
        data_list = time_input_dict.keys()

    # If empty
    if len(data_list) == 0:
        return None

    # Actual query
    df = api.get_time_values(
        data_reference=[time_input_dict[i] for i in data_list],
        start_date=start_date,
        end_date=end_date,
        aggregation=aggregation,
        aggregation_period=aggregation_period,
        aggregation_function=aggregation_function,
        api_credentials=api_credentials,
    )

    # Rename columns
    df = df.rename(columns=utils.reverse_dict(time_input_dict))

    # Output
    return df


def retrieve_batch_steps_and_data(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    batch_type_list: Optional[Union[str, List[str]]] = None,
    batch_type_dict: Optional[dict] = None,
    batch_data_dict: Optional[dict] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    """
    Retrieve batch steps and values into a DataFrame, renaming data in order to be used in a model not knowing the
    actual data references.
    It can be called using a minimal set of arguments, automatically using the current event information.

    Parameters
    ----------
    start_date: str or datetime
        The beginning of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T14:42:00.000Z'
    end_date: str or datetime
        The end of the period to be retrieved. If a string is provided, it should be in ISO format,
        e.g. '2021-01-01T16:42:00.000Z'
    batch_type_list: str or List[str], optional
        A list of batch types aliases to retrieve
    batch_type_dict dict, optional
        A dictionary referencing OIAnalytics batch ids, in the form of {batch_alias: batch_id, ...}
        If None, it is automatically built gathering batch type ids in the current event.
    batch_data_dict: dict, optional
        A dictionary referencing OIAnalytics data references, in the form of {data_alias: data_reference, ...}
        If None, it is automatically built gathering time data references in the current event.
    api_credentials: OIAnalyticsAPICredentials, optional
        The credentials to use to connect to the API. If not provided, default credentials set in environment will
        be used.

    Returns
    -------
    A dictionary where each key is a batch type alias, and each value is a dictionary with two entries:
    - steps: Steps (with dates) of the retrieved batches
    - values: Values and features of the retrieved batches (each data or feature is a column)
    """

    global CURRENT_EVENT
    if batch_type_dict is None:
        batch_type_dict = CURRENT_EVENT.pythonModelInstance.get_input_dict(
            input_types=["BATCH_STRUCTURE"]
        )

    if batch_data_dict is None:
        batch_data_dict = CURRENT_EVENT.pythonModelInstance.get_input_dict(
            input_types=[
                "STORED_BATCH_DATA",
                "BATCH_TAG_KEY",
                "COMPUTED_BATCH_DATA",
                "BATCH_TIME_DATA",
            ]
        )

    if isinstance(batch_type_list, str):
        batch_type_list = [batch_type_list]
    elif batch_type_list is None:
        batch_type_list = batch_type_dict.keys()

    # If empty
    if len(batch_type_list) == 0:
        return None

    # Init
    batches = {}

    # Actual query
    for batch_type in batch_type_list:
        df_steps, df_values = api.get_batch_values(
            batch_type_id=batch_type_dict[batch_type],
            start_date=start_date,
            end_date=end_date,
            api_credentials=api_credentials,
        )

        # Rename data
        df_values = df_values.rename(columns=utils.reverse_dict(batch_data_dict))

        # Append output
        batches[batch_type] = {"steps": df_steps, "data": df_values}

    # Output
    return batches

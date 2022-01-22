# Imports
from typing import List, Optional, Union
from datetime import datetime

import requests

from .. import api

# All
__all__ = [
    "query_data_list",
    "query_data_details",
    "query_time_values",
    "query_batch_types_list",
    "query_batch_type_details",
    "query_batch_values",
]


# Exceptions
class QueryError(Exception):
    """Raised when an endpoint query generate any error"""


# Basic endpoints requests
def query_data_list(
    query: Optional[str] = None,
    types: Optional[List[str]] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data"
    response = requests.get(
        url=url,
        params={"query": query, "type": types, "page": page, "size": size},
        **api_credentials.auth_kwargs(),
    )

    # Output
    return response


def query_data_details(
    data_id: str,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/data/{data_id}"
    response = requests.get(url=url, **api_credentials.auth_kwargs())

    # Output
    return response


def query_time_values(
    data_reference: Union[str, List[str]],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    aggregation: str,
    aggregation_period: Optional[str] = None,
    aggregation_function: Optional[str] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Format dates
    if isinstance(start_date, datetime):
        start_date_iso = f"{start_date.replace(tzinfo=None).isoformat()}Z"
    else:
        start_date_iso = start_date

    if isinstance(end_date, datetime):
        end_date_iso = f"{end_date.replace(tzinfo=None).isoformat()}Z"
    else:
        end_date_iso = end_date

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/time-values/query"
    response = requests.get(
        url=url,
        params={
            "from": start_date_iso,
            "to": end_date_iso,
            "aggregation": aggregation,
            "aggregation-period": aggregation_period,
            "aggregation-function": aggregation_function,
            "data-reference": data_reference,
        },
        **api_credentials.auth_kwargs(),
    )

    # Output
    return response


def query_batch_types_list(
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types"
    response = requests.get(
        url=url,
        params={
            "page": page,
            "size": size,
        },
        **api_credentials.auth_kwargs(),
    )

    # Output
    return response


def query_batch_type_details(
    batch_type_id: str,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}"
    response = requests.get(url=url, **api_credentials.auth_kwargs())

    # Output
    return response


def query_batch_values(
    batch_type_id: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    name: Optional[str] = None,
    tag_values: Optional[Union[str, List[str]]] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
    api_credentials: Optional[api.OIAnalyticsAPICredentials] = None,
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Format dates
    if isinstance(start_date, datetime):
        start_date_iso = f"{start_date.replace(tzinfo=None).isoformat()}Z"
    else:
        start_date_iso = start_date

    if isinstance(end_date, datetime):
        end_date_iso = f"{end_date.replace(tzinfo=None).isoformat()}Z"
    else:
        end_date_iso = end_date

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/batch-types/{batch_type_id}/batches"
    response = requests.get(
        url=url,
        params={
            "start": start_date_iso,
            "end": end_date_iso,
            "name": name,
            "tag-values": tag_values,
            "page": page,
            "size": size,
        },
        **api_credentials.auth_kwargs(),
    )

    # Output
    return response


def insert_time_values(
    data, api_credentials: Optional[api.OIAnalyticsAPICredentials] = None
):
    # Get credentials from environment if not provided
    if api_credentials is None:
        api_credentials = api.get_default_oianalytics_credentials()

    # Query endpoint
    url = f"{api_credentials.base_url}/api/oianalytics/time-values"
    response = requests.post(url=url, data=data, **api_credentials.auth_kwargs())

    # Output
    return response

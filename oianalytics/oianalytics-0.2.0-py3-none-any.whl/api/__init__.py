from typing import Optional

from ._credentials import OIAnalyticsAPICredentials

from . import endpoints

from ._dataframes import (
    get_data_list,
    get_time_values,
    get_batch_types_list,
    get_batch_type_details,
    get_batch_values,
)

# Init
DEFAULT_CREDENTIALS = None


# Default credentials management
def set_default_oianalytics_credentials(
    credentials: Optional[OIAnalyticsAPICredentials] = None,
    base_url: Optional[str] = None,
    login: Optional[str] = None,
    pwd: Optional[str] = None,
    token: Optional[str] = None,
):
    global DEFAULT_CREDENTIALS

    if credentials is not None:
        DEFAULT_CREDENTIALS = credentials
    else:
        DEFAULT_CREDENTIALS = OIAnalyticsAPICredentials(
            base_url=base_url, login=login, pwd=pwd, token=token
        )


def get_default_oianalytics_credentials():
    global DEFAULT_CREDENTIALS
    return DEFAULT_CREDENTIALS

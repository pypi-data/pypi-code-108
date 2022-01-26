"""
Utilities for the rest client
"""
import logging
import typing as t

import pydantic
import requests
import tenacity

from taktile_client.config import arrow_available
from taktile_client.exceptions import (
    APIClientException,
    APIClientExceptionRetryable,
)
from taktile_client.http_client import API

if arrow_available:
    import numpy as np
    import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)

INTERNAL_SERVER_ERROR = (
    requests.codes.INTERNAL_SERVER_ERROR  # pylint: disable=no-member
)
FORBIDDEN = requests.codes.FORBIDDEN  # pylint: disable=no-member
UNAUTHORIZED = requests.codes.UNAUTHORIZED  # pylint: disable=no-member
UNPROCESSABLE_ENTITY = (
    requests.codes.UNPROCESSABLE_ENTITY  # pylint: disable=no-member
)

DO_NOT_RETRY_STATUS_CODES = [
    INTERNAL_SERVER_ERROR,
    FORBIDDEN,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
]


def safe_post(
    *,
    api: API,
    url: str,
    json: t.Optional[t.Any] = None,
    data: t.Optional[t.Any] = None,
    retries: int = 3,
    timeout: float = 30.0,
) -> t.Any:
    """HTTP POST request with retrying

    Parameters
    ----------
    api : API
        the underlying api
    url : str
        url to make the request to
    json: t.Any
        data to be sent
    data: t.Any
        serialized data to be sent
    retries : int
        retries
    timeout : float
        timeout
    """

    def my_after(retry_state: t.Any) -> None:
        logger.warning(
            "Timeout while trying to call endpoint on try #%d/%d: %s",
            retry_state.attempt_number,
            retries,
            retry_state.outcome,
        )

    def my_stop(retry_state: t.Any) -> bool:
        if retry_state.attempt_number >= retries:
            logger.error(
                "Giving up trying to call endpoint after %d attempts",
                retry_state.attempt_number,
            )
            return True
        return False

    @tenacity.retry(
        stop=my_stop,
        retry=tenacity.retry_if_exception_type(  # type: ignore
            exception_types=(APIClientExceptionRetryable,)
        ),
        wait=tenacity.wait_random(min=0, max=1),  # type: ignore
        after=my_after,
        reraise=True,
    )
    def wrapped() -> t.Any:
        try:
            response = api.call(
                verb="post",
                path=url,
                raw=True,
                json=json,
                data=data,
                timeout=timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as err:
            raise APIClientExceptionRetryable(
                status_code=-1, detail="A connection error has occured"
            ) from err

        if response.status_code in DO_NOT_RETRY_STATUS_CODES:
            if response.status_code == INTERNAL_SERVER_ERROR:
                raise APIClientException(
                    status_code=response.status_code,
                    detail="An error occurred with your request. "
                    "Check the deployment's logs for more information",
                )
            if response.status_code == UNPROCESSABLE_ENTITY:
                json_response = response.json()
                raise APIClientException(
                    status_code=response.status_code,
                    detail="Unprocessable request body: "
                    f"{json_response['detail']})",
                )

            json_response = response.json()
            raise APIClientException(
                status_code=response.status_code,
                detail=f"Authentication Error: {json_response['detail']}",
            )
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            try:
                json_response = response.json()
                raise APIClientExceptionRetryable(
                    status_code=response.status_code,
                    detail=json_response["detail"],
                ) from err
            except (ValueError, KeyError) as err:
                # Note that we use ValueError instead of JSONDecodeError above
                # on purpose, because depending on runtime configuration
                # `requests` might choose to use `simplejson` which has a
                # different JSONDecodeError. However both derive from
                # ValueError.
                content = response.text
                raise APIClientExceptionRetryable(
                    status_code=response.status_code,
                    detail=f"An error occurred with your request: {content})",
                ) from err
        return response.json()

    return wrapped()


def is_serializable(payload: t.Any) -> bool:
    """Utility Method to check if payload can be serialized

    Parameters
    ----------
    payload : t.Any
        payload Object
    """
    if arrow_available and isinstance(
        payload, (pd.DataFrame, pd.Series, np.ndarray)
    ):
        serializable = True
    elif isinstance(payload, pydantic.BaseModel):
        serializable = True
    else:
        serializable = False
    return serializable

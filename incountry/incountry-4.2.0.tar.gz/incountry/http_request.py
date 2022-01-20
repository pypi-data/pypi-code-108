from typing import Union

import requests


from .exceptions import (
    StorageAuthenticationException,
    StorageNetworkException,
    StorageServerException,
)


def get_http_response_content(http_response: requests.Response) -> Union[dict, str]:
    try:
        return http_response.json()
    except Exception:
        return http_response.text


def http_request(
    params: dict,
    scope: str = "http request",
    http_code_exception_class: StorageServerException = StorageServerException,
) -> Union[requests.Response, dict, str]:
    try:
        with requests.request(**params) as res:
            if res.status_code == 401:
                raise StorageAuthenticationException(
                    url=params["url"],
                    method=params["method"],
                    status_code=res.status_code,
                    message=res.text,
                    scope=scope,
                )

            if res.status_code >= 400:
                raise http_code_exception_class(
                    url=params["url"],
                    method=params["method"],
                    status_code=res.status_code,
                    message=res.text,
                    scope=scope,
                )

            return (get_http_response_content(res), res)
    except requests.RequestException as e:
        raise StorageNetworkException(
            url=params["url"],
            method=params["method"],
            message=e,
            scope=scope,
        ) from e

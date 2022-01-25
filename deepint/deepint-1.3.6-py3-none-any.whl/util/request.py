#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import requests
from time import sleep

from ..auth import Credentials
from ..error import DeepintHTTPError


def retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3, time_between_tries=10):
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except DeepintHTTPError as e:
                    sleep(time_between_tries)
                    attempt += 1
                    if e.code not in codes:
                        raise e
            return func(*args, **kwargs)

        return newfn

    return decorator


@retry_on(codes=('LIMIT', 'TIMEOUT_ERROR', 'BAD_GATEWAY'), times=3)
def handle_request(credentials: Credentials = None, method: str = None, path: str = None, parameters: dict = None,
                   headers: dict = None, files: tuple = None):
    # build request parameters
    auth_header = {'x-auth-token': credentials.token}
    if headers is None:
        header = headers
    else:
        header = {**auth_header, **headers}

    if parameters is not None:
        parameters = {k: parameters[k] for k in parameters if parameters[k] is not None}

    # prepare request parts
    url = f'https://{credentials.instance}{path}'
    params = parameters if method == 'GET' else None
    data = parameters if method != 'GET' and files is not None else None
    json_data = parameters if method != 'GET' and files is None else None

    # perform request
    response = requests.request(method=method, url=url, headers=header, params=params, json=json_data, data=data, files=files)

    if response.status_code == 500:
        raise DeepintHTTPError(code='UNKOWN_ERROR',
                               message='System errored. Please, wait a few seconds and try again.',
                               method=method, url=url)
    elif response.status_code == 504:
        raise DeepintHTTPError(code='TIMEOUT_ERROR',
                               message='System reached maximum timeout in the request processing. Please, wait a few seconds and try again.',
                               method=method, url=url)
    elif response.status_code == 502:
        raise DeepintHTTPError(code='BAD_GATEWAY',
                               message='Unable to estabilish connection to system. Please, wait a few seconds and try again.',
                               method=method, url=url)

    # retrieve information
    try:
        response_json = response.json()
    except:
        raise DeepintHTTPError(code=response.status_code, message='The API returned a no JSON-deserializable response.', method=method, url=url)

    if response.status_code != 200:
        raise DeepintHTTPError(code=response_json['code'], message=response_json['message'], method=method, url=url)

    return response_json


def handle_paginated_request(credentials: Credentials = None, method: str = None, path: str = None,
                             headers: dict = None, parameters: dict = None, files: tuple = None):
    # first response
    response = handle_request(credentials=credentials, method=method, path=path, parameters=parameters, headers=headers, files=files)

    # update state and return items
    yield from response['items']
    next_page = response['page'] + 1
    total_pages = response['pages_count']

    # create parameters    
    parameters = parameters if parameters is not None else {}

    # request the rest of the data
    while next_page < total_pages:
        # update parameters and perform request
        parameters['page'] = next_page
        response = handle_request(credentials=credentials, method=method, path=path, headers=headers, parameters=parameters, files=files)

        # update state and return items
        yield from response['items']
        next_page = response['page'] + 1
        total_pages = response['pages_count']

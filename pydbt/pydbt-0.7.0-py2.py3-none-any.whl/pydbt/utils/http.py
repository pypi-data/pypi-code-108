import time
import requests
import typing as T
from ..logger import GLOBAL_LOGGER as log
from .tools import get_elapsed_milliseconds_since


def make_external_call(
        method: str, url: str, *, service_name: str = 'external service',
        raise_exception: bool = True, log_error: bool = True, **kwargs
) -> T.Union[str, None, Exception]:
    """A generic wrapper for handling external calls better-ish."""
    request_data = {}
    if kwargs.get('json'):
        request_data = kwargs['json']
    elif kwargs.get('params'):
        request_data = kwargs['params']

    start_time = time.time()
    try:
        # set default timeout of 30 secs if a value is not passed in
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30

        response = requests.request(method, url, **kwargs)
        # check that we get a 2xx response from the external service
        response.raise_for_status()

        # create log payload
        log_payload = {
            'total_time': get_elapsed_milliseconds_since(start_time),
            'request_url': response.url.split('/')[2],
            'response_status': response.status_code
        }

        log.info(f'Call to {service_name} was successful', payload=log_payload)

        if 'json' in response.headers.get('Content-Type'):
            return response.json()
        else:
            return response.text

    except Exception as e:
        # log error
        if log_error:
            log_payload = {
                'total_time': get_elapsed_milliseconds_since(start_time),
                'request_data': request_data
            }

            log.error(
                f'{service_name} error',
                exception=e,
                payload=log_payload
            )

        # raise exception
        if raise_exception:
            raise e
        else:
            return None

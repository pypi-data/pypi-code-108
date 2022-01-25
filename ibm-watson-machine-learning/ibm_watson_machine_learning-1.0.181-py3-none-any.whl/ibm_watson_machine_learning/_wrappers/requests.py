import os
import requests
from requests import packages, exceptions
from functools import wraps

verify = os.environ.get('WML_CLIENT_VERIFY_REQUESTS')

def set_verify_for_requests(func):
    @wraps(func)
    def wrapper(*args, **kw):
        global verify

        if verify is not None:
            if verify == 'True':
                kw.update({'verify': True})

            elif verify == 'False':
                kw.update({'verify': False})

            else:
                kw.update({'verify': verify})

        else:
            kw.update({'verify': True})

        try:
            res = func(*args, **kw)

        except OSError as e:

            # User can pass verify the path to a CA_BUNDLE file or directory with certificates of trusted CAs
            if isinstance(verify, str):
                raise OSError(f"Connection cannot be verified with default trusted CAs. "
                              f"Please provide correct path to a CA_BUNDLE file or directory with "
                              f"certificates of trusted CAs. Error: {e}")

            # forced verify to True
            elif verify:
                raise e

            # default
            elif verify is None:
                verify = 'False'
                kw.update({'verify': False})
                res = func(*args, **kw)

            # disabled verify
            else:
                raise e

        return res

    return wrapper


@set_verify_for_requests
def get(url, params=None, **kwargs):
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.get(url=url, params=params, **kwargs)


@set_verify_for_requests
def options(url, **kwargs):
    r"""Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.options(url=url, **kwargs)


@set_verify_for_requests
def head(url, **kwargs):
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.head(url=url, **kwargs)


@set_verify_for_requests
def post(url, data=None, json=None, **kwargs):
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.post(url=url, data=data, json=json, **kwargs)


@set_verify_for_requests
def put(url, data=None, **kwargs):
    r"""Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.put(url=url, data=data, **kwargs)


@set_verify_for_requests
def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.patch(url=url, data=data, **kwargs)


@set_verify_for_requests
def delete(url, **kwargs):
    r"""Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return requests.delete(url=url, **kwargs)

import traceback

from requests import *  # noqa: F403, F401
from requests import Session, Request

from security.logging.requests.logger import OutputRequestLogger


class SecuritySession(Session):

    def __init__(self, slug=None, related_objects=None):
        super().__init__()
        self.slug = slug
        self.related_objects = [] if related_objects is None else related_objects

    def request(self, method, url, params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None,
                json=None, slug=None, related_objects=None):

        related_objects = [] if related_objects is None else related_objects

        # Create the Request.
        req = Request(
            method=method.upper(), url=url, headers=headers, files=files, data=data or {}, json=json,
            params=params or {}, auth=auth, cookies=cookies, hooks=hooks,
        )
        prep = self.prepare_request(req)
        proxies = proxies or {}
        request_settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )
        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(request_settings)

        with OutputRequestLogger(related_objects=related_objects or self.related_objects,
                                 slug=slug or self.slug) as output_request_logger:
            output_request_logger.log_request(prep)
            try:
                response = self.send(prep, **send_kwargs)
                output_request_logger.log_response(response)
                return response
            except Exception:
                output_request_logger.log_exception(traceback.format_exc())
                raise


def request(method, url, **kwargs):
    with SecuritySession() as session:
        return session.request(method=method, url=url, **kwargs)


def get(url, params=None, **kwargs):
    """Sends a GET request.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    """Sends a OPTIONS request.
    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    """Sends a HEAD request.
    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    """Sends a POST request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    """Sends a PUT request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    """Sends a PATCH request.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    """Sends a DELETE request.
    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request('delete', url, **kwargs)

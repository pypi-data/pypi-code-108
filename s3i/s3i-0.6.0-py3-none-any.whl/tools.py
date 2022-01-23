import urllib


def http_error_from_request_response(response):
    """Returns an urllib.error.HTTPError created from a requests.Response
    object.

    :type response: requests.Response
    :rtype: urllib.error.HTTPError

    """
    error = urllib.error.HTTPError(
        code=response.status_code,
        msg=response.text,
        hdrs=response.headers,
        fp=None,
        url=response.url,
    )
    return error

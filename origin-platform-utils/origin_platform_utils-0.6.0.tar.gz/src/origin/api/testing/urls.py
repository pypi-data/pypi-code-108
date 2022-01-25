from typing import Optional
from urllib.parse import urlparse, parse_qs


def assert_base_url(
        url: str,
        expected_base_url: str,
        check_path: bool = True,
):
    """
    Asserts that a given [absolute] URL has the expected base URL,
    ie. the protocol and domain parts.

    Example of tests that will pass::

        assert_base_url('http://foo.com', 'http://foo.com')
        assert_base_url('https://foo.com?query=value', 'https://foo.com')

    Examples of tests that will fail::

        assert_has_base_url('http://bar.com', 'http://bar.com')
        assert_has_base_url('https://bar.com?query=value', 'https://bar.com')

    :param url: The URL to test
    :param expected_base_url: The base-URL to match
    :param check_path: Whether or not the assert on the path also
    """
    url_parsed = urlparse(url)
    expected_url_parsed = urlparse(expected_base_url)

    error_msg = f'URL mismatch: {url} != {expected_base_url}'

    assert url_parsed.scheme == expected_url_parsed.scheme, error_msg
    assert url_parsed.netloc == expected_url_parsed.netloc, error_msg

    if check_path:
        assert url_parsed.path == expected_url_parsed.path, error_msg
        assert url_parsed.params == expected_url_parsed.params, error_msg


def assert_query_parameter(
        url: str,
        name: str,
        value: Optional[str] = None,
):
    """
    Asserts that a given [absolute] URL has the expected query parameter
    present. Optionally asserts the value of the parameter, otherwise only
    assert the existence of the parameter.

    Example of tests that will pass::

        assert_query_parameter('http://foo.com?query=value', 'query')
        assert_query_parameter('http://foo.com?query=value', 'query', 'value')

    Examples of tests that will fail::

        assert_query_parameter('http://bar.com?query=value', 'foo')
        assert_query_parameter('http://bar.com?query=value', 'query', 'bar')

    :param url: The URL to test
    :param name: Name of the query parameter
    :param value: Value of the query parameter to match, or None
    """
    url_parsed = urlparse(url)
    query_parsed = parse_qs(url_parsed.query)

    assert name in query_parsed, \
        f'Query parameter "{name}" not found in: {query_parsed}'

    if value is not None:
        assert query_parsed[name] == [value], (
            f'Value for query parameter {name} mismatch: '
            f'{query_parsed[name]} != {value}'
        )

"""unittest module"""
from mc_automation_tools import base_requests, common


def test_url_validation():
    """
    This check url validation util with variants strings
    """
    assert common.url_validator("http://www.google.com")  # true
    assert common.url_validator("https://www.google.com")  # true
    assert common.url_validator("http://google.com")  # true
    assert common.url_validator("http://google.com")  # true
    assert common.url_validator("http://www.google.co.uk")  # true
    assert common.url_validator("http://www.google.dk")
    assert not common.url_validator("wwww.google.com")
    assert not common.url_validator("www.google")
    assert not common.url_validator("google")
    assert not common.url_validator("htp://www.google.com")
    assert not common.url_validator("www.google.com")  # true


def test_combine_url():
    """
    This check url combination by base url + *args
    """
    base_url = "http://www.google.com"
    arg1 = "my"
    arg2 = "test"
    arg3 = "url"
    arg4 = "is"
    arg5 = "work"
    combined1 = "http://www.google.com/my/test/url"
    combined2 = "http://www.google.com/my/test/url/is"
    combined3 = "http://www.google.com/my/test/url/is/work"
    assert combined1 == common.combine_url(base_url, arg1, arg2, arg3)
    assert combined2 == common.combine_url(base_url, arg1, arg2, arg3, arg4)
    assert combined3 == common.combine_url(base_url, arg1, arg2, arg3, arg4, arg5)


def test_response_parser():
    """
    parsing standard request response
    """
    mock_response = base_requests.send_get_request("http://www.google.com")
    status_code, content = common.response_parser(mock_response)
    assert status_code
    assert content


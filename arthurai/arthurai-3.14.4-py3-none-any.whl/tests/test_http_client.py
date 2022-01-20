from copy import deepcopy
from io import BytesIO
from typing import Dict, NamedTuple, Callable

import pytest
import requests
import json
import inspect
from platform import system

from pytest_httpserver import HTTPServer, HeaderValueMatcher
from pytest import mark

from arthurai.client.http.arthur import ArthurHTTPClient
from arthurai.client.http.base import AbstractHTTPClient
from arthurai.client.http.requests import HTTPClient
from arthurai import __version__ as arthur_version


# CONSTANTS
from tests import MockResponse

MULTIPART_HEADER_PREFIX = "multipart/form-data; boundary="

# FIXTURES
# to be supplied
ACCESS_KEY = "abc123"
SAMPLE_DATA = {'foo': "bar",
               'baz': 2}
ARRAY_DATA = [1, 2, 3]
SAMPLE_DATA_BYTES = bytes(json.dumps(SAMPLE_DATA), encoding='utf-8')
ARRAY_DATA_BYTES = bytes(json.dumps(ARRAY_DATA), encoding='utf-8')
NESTED_DATA = {'data': json.dumps(SAMPLE_DATA), 'other_data': ARRAY_DATA}
NESTED_DATA_BYTES = {'data': SAMPLE_DATA_BYTES, 'other_data': ARRAY_DATA_BYTES}
PARAMS = {'query': "param"}
SAMPLE_FILE_DATA = {
    "file.name": bytes("hello im mr data", encoding="utf-8"),
    "other.file": bytes("and im other data", encoding="utf-8"),
}

# to be returned
ORG_ID = "org123"
ORG_ID_RESPONSE = {'organization_id': ORG_ID}

# headers
INITIAL_HEADERS = {
    "Authorization": ACCESS_KEY,
    "Accept": "application/json"
}
JSON_HEADERS = {
    **INITIAL_HEADERS, "Content-Type": "application/json"}
MULTIPART_HEADERS = {
    **INITIAL_HEADERS, "Content-Type": "multipart/form-data"
}

EXPECTED_USER_AGENT = f"arthur-sdk/{arthur_version} (system={system()}, org={ORG_ID})"


def given_arthur_http_client(httpserver: HTTPServer) -> ArthurHTTPClient:
    base_url = httpserver.url_for("")
    return ArthurHTTPClient(access_key=ACCESS_KEY, url=base_url, base_path='/api/v3', verify_ssl=True)


def given_requests_http_client(httpserver: HTTPServer) -> HTTPClient:
    base_url = httpserver.url_for("")
    headers = {
        'Accept': "application/json",
        'Authorization': ACCESS_KEY,
        'User-Agent': EXPECTED_USER_AGENT,
    }
    return HTTPClient(base_url=base_url, path_prefix="/api", default_headers=headers, verify_ssl=True)


"""
TIP:
The pytest_httpserver lib is generally great but a little annoying because if there's no match you just get back a 
generic "no matcher found" response. I suggest dropping a breakpoint in the httpserver.py/RequestMatcher.match()
method if you're trying to diagnose errors.
"""


class TestHTTPClientCase(NamedTuple):
    given_client: Callable[[HTTPServer], AbstractHTTPClient]
    user_agent: str
    api_prefix: str
    extra_requests_count: int
    multipart_requires_content_type: bool


CASES = [
    pytest.param(
        TestHTTPClientCase(given_client=given_arthur_http_client, user_agent=EXPECTED_USER_AGENT, api_prefix="",
                           extra_requests_count=1, multipart_requires_content_type=True), id="arthur-http-client"),
    pytest.param(
        TestHTTPClientCase(given_client=given_requests_http_client, user_agent=EXPECTED_USER_AGENT, api_prefix="/api",
                           extra_requests_count=0, multipart_requires_content_type=False), id="requests-http-client")
]


@mark.parametrize("case", CASES)
def test_client_method_signatures_match(httpserver: HTTPServer, case: TestHTTPClientCase):
    allowed_method_name_differences = {"endpoint": "url"}
    abstract_methods = AbstractHTTPClient.__abstractmethods__
    target_class = inspect.signature(case.given_client).return_annotation
    for method_name in abstract_methods:
        abstract_signature = inspect.signature(AbstractHTTPClient.__getattribute__(AbstractHTTPClient, method_name))
        concrete_signature = inspect.signature(target_class.__getattribute__(target_class, method_name))
        concrete_signature_list = list(concrete_signature.parameters.items())
        i = 0
        for abstract_name, abstract_param in abstract_signature.parameters.items():
            if abstract_param.kind.name == "POSITIONAL_ONLY":
                concrete_name, concrete_param = concrete_signature_list[i]
            elif abstract_param.kind.name in ("KEYWORD_ONLY", "POSITIONAL_OR_KEYWORD"):
                if abstract_name in concrete_signature.parameters.keys():
                    concrete_name = abstract_name
                elif abstract_name in allowed_method_name_differences.keys() and allowed_method_name_differences[abstract_name] in concrete_signature.parameters.keys():
                    concrete_name = allowed_method_name_differences[abstract_name]
                else:
                    raise AssertionError(f"abstract method '{method_name}' keyword parameter '{abstract_name}' not in "
                                         "concrete implementation")
                concrete_param = concrete_signature.parameters[concrete_name]
            elif abstract_param.kind.name in ("VAR_KEYWORD", "VAR_POSITIONAL"):
                continue
            else:
                raise ValueError(f"can't interpret paramter type {abstract_param.kind.name}")

            if abstract_param.default != inspect._empty:  # type: ignore
                assert concrete_param.default == abstract_param.default
            i += 1


@mark.parametrize("case", CASES)
def test_get(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    # allow the client to include an application/json Content-Type header even though it shouldn't
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(INITIAL_HEADERS, case.user_agent),
                                      query_string=PARAMS) \
        .respond_with_json({'status': "ok"})
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      query_string=PARAMS) \
        .respond_with_json({'status': "ok"})

    response = client.get("/test", params=PARAMS, return_raw_response=True)

    assert response.status_code < 300
    assert len(httpserver.log) == 1 + case.extra_requests_count


@mark.parametrize("case", CASES)
def test_delete(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    # allow the client to include an application/json Content-Type header even though it shouldn't
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="DELETE",
                                      headers=add_user_agent_header(INITIAL_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="DELETE",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})

    response = client.delete("/test", return_raw_response=True)

    assert response.status_code < 300
    assert len(httpserver.log) == 1 + case.extra_requests_count


@mark.parametrize("case", CASES)
def test_json_post(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    data_copy = deepcopy(SAMPLE_DATA)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST", json=SAMPLE_DATA,
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})

    response = client.post("/test", json=SAMPLE_DATA, return_raw_response=True)

    assert response.status_code < 300
    assert len(httpserver.log) == 1 + case.extra_requests_count
    # inputs not modified
    assert data_copy == SAMPLE_DATA


@mark.parametrize("case", CASES)
def test_multipart_post(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    sample_files = sample_file_data_to_files_map(SAMPLE_FILE_DATA)

    # header matchers, kinda weird API but this does the trick
    multipart_header_matcher = HeaderValueMatcher(matchers={
        **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
        'User-Agent': HeaderValueMatcher.default_header_value_matcher,
        'Content-Type': match_multipart_headers
    })

    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher,
                                      headers=add_user_agent_header(MULTIPART_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})

    # our client makes you specify multipart in the headers yourself, otherwise it wont send the files you supply
    base_headers = {'Content-Type': "multipart/form-data"} if case.multipart_requires_content_type else {}
    response = client.post("/test", json=None, files=sample_files,
                           headers=add_user_agent_header(base_headers, case.user_agent),
                           return_raw_response=True)

    assert response.status_code < 300
    request = httpserver.log[-1][0]
    assert_multipart_expected(request, files_map=sample_files, data_map={})
    assert len(httpserver.log) == 1 + case.extra_requests_count


@mark.parametrize("case", CASES)
def test_multipart_post_retry(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    sample_files = sample_file_data_to_files_map(SAMPLE_FILE_DATA)

    # header matchers, kinda weird API but this does the trick
    multipart_header_matcher = HeaderValueMatcher(matchers={
        **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
        'User-Agent': HeaderValueMatcher.default_header_value_matcher,
        'Content-Type': match_multipart_headers
    })

    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher,
                                      headers=add_user_agent_header(MULTIPART_HEADERS, case.user_agent)) \
        .respond_with_json({'errors': "no bad"}, status=500)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher,
                                      headers=add_user_agent_header(MULTIPART_HEADERS, case.user_agent)) \
        .respond_with_json({'message': "ok"})

    # our client makes you specify multipart in the headers yourself, otherwise it wont send the files you supply
    base_headers = {'Content-Type': "multipart/form-data"} if case.multipart_requires_content_type else {}
    response = client.post("/test", json=None, files=sample_files,
                           headers=add_user_agent_header(base_headers, case.user_agent), retries=1,
                           return_raw_response=True)

    assert response.status_code < 300
    request = httpserver.log[-1][0]
    assert_multipart_expected(request, files_map=sample_files, data_map={})
    assert len(httpserver.log) == 2 + case.extra_requests_count


@mark.parametrize("case", CASES)
def test_multipart_post_mixed_retry(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    sample_files = sample_file_data_to_files_map(SAMPLE_FILE_DATA)

    # header matchers, kinda weird API but this does the trick
    multipart_header_matcher = HeaderValueMatcher(matchers={
        **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
        'User-Agent': HeaderValueMatcher.default_header_value_matcher,
        'Content-Type': match_multipart_headers
    })

    data_copy = deepcopy(NESTED_DATA)

    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher,
                                      headers=add_user_agent_header(MULTIPART_HEADERS, case.user_agent)) \
        .respond_with_json({'errors': "no bad"}, status=500)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher,
                                      headers=add_user_agent_header(MULTIPART_HEADERS, case.user_agent)) \
        .respond_with_json({'message': "ok"})

    # our client makes you specify multipart in the headers yourself, otherwise it wont send the files you supply
    base_headers = {'Content-Type': "multipart/form-data"} if case.multipart_requires_content_type else {}
    response = client.post("/test", json=NESTED_DATA, files=sample_files,
                           headers=add_user_agent_header(base_headers, case.user_agent), retries=1,
                           return_raw_response=True)

    assert response.status_code < 300
    request = httpserver.log[-1][0]
    assert_multipart_expected(request, files_map=sample_files, data_map=NESTED_DATA_BYTES)
    assert len(httpserver.log) == 2 + case.extra_requests_count
    # inputs not modified
    assert data_copy == NESTED_DATA


@mark.parametrize("case", CASES)
def test_multipart_post_nofiles(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    data_copy = deepcopy(NESTED_DATA)

    # header matchers, kinda weird API but this does the trick
    multipart_header_matcher = HeaderValueMatcher(matchers={
        **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
        'User-Agent': HeaderValueMatcher.default_header_value_matcher,
        'Content-Type': match_multipart_headers
    })

    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="POST",
                                      header_value_matcher=multipart_header_matcher, headers=MULTIPART_HEADERS) \
        .respond_with_json({'status': "ok"})

    response = client.post("/test", json=NESTED_DATA,
                           headers=add_user_agent_header({'Content-Type': "multipart/form-data"}, case.user_agent),
                           return_raw_response=True)

    assert response.status_code < 300
    request = httpserver.log[-1][0]
    assert_multipart_expected(request, data_map=NESTED_DATA_BYTES)
    assert len(httpserver.log) == 1 + case.extra_requests_count
    # inputs not modified
    assert data_copy == NESTED_DATA


@mark.parametrize("case", CASES)
def test_json_patch(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    data_copy = deepcopy(SAMPLE_DATA)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="PATCH", json=SAMPLE_DATA,
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})

    response = client.patch("/test", json=SAMPLE_DATA, return_raw_response=True)

    assert response.status_code < 300
    assert len(httpserver.log) == 1 + case.extra_requests_count
    # inputs not modified
    assert data_copy == SAMPLE_DATA


@mark.parametrize("case", CASES)
def test_multipart_patch_mixed(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    sample_files = sample_file_data_to_files_map(SAMPLE_FILE_DATA)

    # header matchers, kinda weird API but this does the trick
    multipart_header_matcher = HeaderValueMatcher(matchers={
        **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
        'Content-Type': match_multipart_headers
    })

    data_copy = deepcopy(NESTED_DATA)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="PATCH",
                                      header_value_matcher=multipart_header_matcher, headers=MULTIPART_HEADERS) \
        .respond_with_json({'status': "ok"})

    response = client.patch("/test", json=NESTED_DATA, files=sample_files,
                            headers=add_user_agent_header({'Content-Type': "multipart/form-data"}, case.user_agent),
                            return_raw_response=True)

    assert response.status_code < 300
    request = httpserver.log[-1][0]
    assert_multipart_expected(request, files_map=sample_files, data_map=NESTED_DATA_BYTES)
    assert len(httpserver.log) == 1 + case.extra_requests_count
    # inputs not modified
    assert data_copy == NESTED_DATA


@mark.parametrize("case", CASES)
def test_put(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    data_copy = deepcopy(SAMPLE_DATA)
    httpserver.expect_oneshot_request(f"{case.api_prefix}/test", method="PUT", json=SAMPLE_DATA,
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent)) \
        .respond_with_json({'status': "ok"})

    response = client.put("/test", json=SAMPLE_DATA, return_raw_response=True)

    assert response.status_code < 300
    # one for get org and one for current
    assert len(httpserver.log) == 1 + case.extra_requests_count
    # inputs not modified
    assert data_copy == SAMPLE_DATA


@mark.parametrize("case", CASES)
def test_retries_validation(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    # headers
    def allow_none_match(actual: str, expected: str) -> bool:
        return (actual == expected) or actual is None
    allow_none_matcher = HeaderValueMatcher(matchers={
            **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
            'User-Agent': HeaderValueMatcher.default_header_value_matcher,
            'Content-Type': allow_none_match
        })

    # 400 response
    bad_request_response = MockResponse("bad request", 400)
    internal_error_response = MockResponse("internal server error", 500)

    if 'validation_response_code' in inspect.signature(client.send).parameters.keys():
        additional_args = {'validation_response_code': 200}
    else:
        additional_args = {}

    # two failures then one success
    httpserver.expect_ordered_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      header_value_matcher=allow_none_matcher) \
        .respond_with_response(bad_request_response)
    httpserver.expect_ordered_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      header_value_matcher=allow_none_matcher) \
        .respond_with_response(internal_error_response)
    httpserver.expect_ordered_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      header_value_matcher=allow_none_matcher) \
        .respond_with_json({'status': "ok"})

    response = client.send("/test", method="GET", return_raw_response=True, retries=2, **additional_args)

    assert response.status_code < 300
    assert len(httpserver.log) == 3 + case.extra_requests_count


@mark.parametrize("case", CASES)
def test_retries_validation_failure(httpserver: HTTPServer, case: TestHTTPClientCase):
    given_orgid_returned(httpserver)
    client = case.given_client(httpserver)

    # headers
    def allow_none_match(actual: str, expected: str) -> bool:
        return (actual == expected) or actual is None
    allow_none_matcher = HeaderValueMatcher(matchers={
            **{header: HeaderValueMatcher.default_header_value_matcher for header in INITIAL_HEADERS.keys()},
            'User-Agent': HeaderValueMatcher.default_header_value_matcher,
            'Content-Type': allow_none_match
        })

    # 400 response
    bad_request_response = MockResponse("bad request", 400)
    internal_error_response = MockResponse("internal server error", 500)

    if 'validation_response_code' in inspect.signature(client.send).parameters.keys():
        additional_args = {'validation_response_code': 200}
    else:
        additional_args = {}

    # two failures then one success
    httpserver.expect_ordered_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      header_value_matcher=allow_none_matcher) \
        .respond_with_response(bad_request_response)
    httpserver.expect_ordered_request(f"{case.api_prefix}/test", method="GET",
                                      headers=add_user_agent_header(JSON_HEADERS, case.user_agent),
                                      header_value_matcher=allow_none_matcher) \
        .respond_with_response(internal_error_response)

    exception = None
    response = None
    try:
        response = client.send("/test", method="GET", return_raw_response=True, retries=1, **additional_args)
    except Exception as e:
        exception = e

    assert exception is not None or (response is not None and response.status_code == 500)
    assert len(httpserver.log) == 2 + case.extra_requests_count


def add_user_agent_header(original_headers, user_agent):
    return {
        **original_headers,
        "User-Agent": user_agent
    }


def given_orgid_returned(httpserver: HTTPServer) -> None:
    # allow the client to include an application/json Content-Type header even though it shouldn't
    headers = {**INITIAL_HEADERS, "Content-Type": "application/json"}
    user_agent = f"python-requests/{requests.__version__}"
    httpserver.expect_oneshot_request("/api/v3/users/me", method="GET",
                                      headers=add_user_agent_header(headers, user_agent)) \
        .respond_with_json(ORG_ID_RESPONSE)
    httpserver.expect_oneshot_request("/api/v3/users/me", method="GET",
                                      headers=add_user_agent_header(INITIAL_HEADERS, user_agent)) \
        .respond_with_json(ORG_ID_RESPONSE)


def match_multipart_headers(actual: str, expected: str) -> bool:
    return actual.startswith("multipart/form-data; boundary=")


def sample_file_data_to_files_map(sample_data: Dict[str, bytes]) -> Dict[str, BytesIO]:
    return {
        fname: BytesIO(content) for fname, content in sample_data.items()
    }


def assert_multipart_expected(request: requests.Request, files_map: Dict[str, BytesIO] = None,
                              data_map: Dict[str, bytes] = None) -> None:
    if files_map is None:
        files_map = {}
    if data_map is None:
        data_map = {}
    boundary = request.headers['Content-Type'][len(MULTIPART_HEADER_PREFIX):]
    prefix = bytes(f"--{boundary}", encoding="utf-8")

    data = request.data
    assert data is not None
    assert isinstance(data, bytes)
    assert data.startswith(prefix)

    blocks = data.split(prefix)

    # build map from expected content to count of instances
    block_counts_map = {}
    for filename, content in files_map.items():
        content.seek(0)
        expected_block = bytes(f'\r\nContent-Disposition: form-data; name="{filename}"; filename="{filename}"\r\n\r\n',
                               encoding='utf-8') + content.read() + bytes("\r\n", encoding='utf-8')
        block_counts_map[expected_block] = 0
    for keyname, data in data_map.items():
        expected_block = bytes(f'\r\nContent-Disposition: form-data; name="{keyname}"\r\n\r\n',
                               encoding='utf-8') + data + bytes("\r\n", encoding='utf-8')
        block_counts_map[expected_block] = 0

    # first block should be empty per startswith() assertion above, iterate through content blocks
    # go through each subsequent block, it should be in our map
    for block in blocks[1:-1]:
        assert block in block_counts_map.keys()
        block_counts_map[block] += 1

    # ensure each block was seen exactly once
    for count in block_counts_map.values():
        assert count == 1

    # validate ends with expected suffix
    assert blocks[-1] == bytes("--\r\n", encoding='utf-8')

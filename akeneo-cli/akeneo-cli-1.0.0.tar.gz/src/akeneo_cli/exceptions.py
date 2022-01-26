import json
import logging


class Akeneo_Exception(Exception):
    pass


class Akeneo_RequestException(Akeneo_Exception):

    response = None

    def __init__(self, response):
        self.response = response
        request_body = response.request.body
        status_code = response.status_code
        if response.headers["content-type"] == "application/json":
            response_body = response.json()
        else:
            response_body = response.text
        super().__init__(
            f"ERROR {status_code} {response.request.method} {response.url}\nData sent : {request_body}\nData recieved : {response_body}"
        )


class Akeneo_NotFound(Akeneo_RequestException):
    pass


class Akeneo_UnexpectedResponse(Akeneo_Exception):

    expect = None
    got = None

    def __init__(self, expect, got):
        self.expect = expect
        self.got = got
        super().__init__("Key %s not found in %s" % (expect, got))

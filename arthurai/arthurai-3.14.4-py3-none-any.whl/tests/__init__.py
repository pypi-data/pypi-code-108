from requests import Response


class MockResponse(Response):
    def __init__(self, response_object, status_code: int):
        self.status_code = status_code
        self.response_object = response_object

    def json(self):
        return self.response_object

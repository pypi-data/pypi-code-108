from abc import ABC
from typing import Generic, TypeVar

from requests import Response, Session

from pytestapilib.http.builder import RequestBuilder
from pytestapilib.http.log import ResponseLogger


class BaseResponse(ABC):

    def __init__(self, response: Response):
        self.response = response

    def get_body(self):
        return self.response.json()


TObj = TypeVar("TObj", bound=BaseResponse)


class BaseRequest(ABC, Generic[TObj]):

    def __init__(self):
        self.request = None

    def send(self, session: Session) -> Response:
        prep_request = RequestBuilder(session, self.request).intercept()
        response = session.send(prep_request)
        ResponseLogger(response).log()
        return response

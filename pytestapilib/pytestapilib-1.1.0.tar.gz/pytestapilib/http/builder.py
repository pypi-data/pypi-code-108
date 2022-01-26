import os

from requests import PreparedRequest, Request, Session

from pytestapilib.core.config import WireMockConfig
from pytestapilib.core.log import log


class RequestBuilder:
    def __init__(self, session: Session, request: Request):
        self.prep_request = request.prepare()
        self.prep_request.url = session.params["url"] + self.prep_request.path_url
        self.current_pytest = os.environ.get('PYTEST_CURRENT_TEST')

    def intercept(self) -> PreparedRequest:
        if WireMockConfig.ENABLED:
            log.debug("Intercept request %s %s for %s test", self.prep_request.method, self.prep_request.url,
                      self.current_pytest)
            wiremock_base_url = WireMockConfig.HOST + ':' + str(WireMockConfig.PORT)
            self.prep_request.url = wiremock_base_url + self.prep_request.path_url
            self.prep_request.headers['Test-Name-Header'] = self.current_pytest
        return self.prep_request

from requests import Response

from pytestapilib.core.log import log


class ResponseLogger:
    def __init__(self, response: Response):
        self.response = response

    def log(self):
        log.debug(f"""
        Request-Response:
        {self.response.request.method} {self.response.request.url}
        {self.response.request.headers}
        {self.response.request.body}

        {self.response.status_code}
        {self.response.headers}
        {self.response.text}
        """)

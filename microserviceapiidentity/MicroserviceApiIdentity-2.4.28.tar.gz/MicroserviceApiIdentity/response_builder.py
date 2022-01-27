"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
from flask import make_response, jsonify


class ResponseBuilder:
    """
    >>> return ResponseBuilder(None, (200, "MS-0000", "Success.")).get_response()
    """
    payload = None
    meta = dict()
    status = 200
    cookie = dict()

    def __init__(self, payload, status):
        self.payload = payload
        self.status = status

    def set_cookie(self, key, value):
        self.cookie[key] = value

    def set_payload(self, payload):
        self.payload = payload

    @classmethod
    def set_meta(cls, key, value):
        cls.meta[key] = value

    def get_response(self):
        """Метод строит стандартизированный ответ
        """
        content = {
            "status": {
                "code": self.status[1],
                "message": self.status[2],
                "severity": self.status[3]
            }
        }
        if self.payload:
            content['payload'] = self.payload

        if len(self.meta) > 0:
            for meta in self.meta:
                content['meta'][meta] = self.meta[meta]

        response = make_response(
            jsonify(content),
            int(self.status[0])
        )
        response.headers["Content-Type"] = "application/json"

        if len(self.cookie) > 0:
            for cook in self.cookie:
                response.set_cookie(cook, value=self.cookie[cook])

        return response

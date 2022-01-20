import json


class ZerohashResponse:
    def __init__(self, body, code, headers):

        self.body = body
        self.code = code
        self.headers = headers
        json_body = json.loads(body)
        self.data = json_body.get("message") or json_body

        if "page" in json_body:
            self.page = json_body["page"]

        if "total_pages" in json_body:
            self.total_pages = json_body["total_pages"]

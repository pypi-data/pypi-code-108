class AppyxHttpResponse:
    def __init__(self, http_status_code, description, content):
        self._http_status_code = http_status_code
        self._description = description
        self._content = content

    def http_status_code(self):
        return self._http_status_code

    def description(self):
        return self._description

    def content(self):
        return self._content

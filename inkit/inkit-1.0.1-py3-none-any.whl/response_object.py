from inkit.extensions import flat


class ResponseObject:

    def __init__(self, resp):
        self.response = resp
        self.content_type = resp.headers['content-type']
        self.status_code = resp.status_code
        self.content = resp.content
        self.text = resp.text
        self._json = None

        if self.text and self.content_type == 'application/json':
            self._json = resp.json()

        self.data = flat(self._json)

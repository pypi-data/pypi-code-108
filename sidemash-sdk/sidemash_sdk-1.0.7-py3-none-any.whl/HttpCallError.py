
class HttpCallError(Exception):

    def __init__(self, status_code: int, status_message: str, body: str):
        self.status_code = status_code
        self.status_message = status_message
        self.body = body

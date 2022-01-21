class HTTPError(Exception):
    def __init__(self, mm_error):
        self.status_code = mm_error.status_code
        self.fields = mm_error.fields
        self.message = mm_error.message

import time


class SdmRequest:

    def __init__(self, signed_headers, method, path, query_string, body_hash):
        self.nonce = int(round(time.time() * 1000))
        self.signed_headers = signed_headers
        self.method = method
        self.path = path
        self.query_string = query_string
        self.body_hash = body_hash

    def to_message(self):
        return (
            str(self.nonce) +
            "".join([name + ":" + value for name, value in list(self.signed_headers.items()) ]) +
            self.method +
            self.path +
            (self.query_string if self.query_string is not None else "") +
            (self.body_hash if self.body_hash is not None else "")
        )

SUCCESS = "success"
FAIL = "fail"
STATUS_STATES = [SUCCESS, FAIL]


class DKReturnCode(object):
    def __init__(self, status, message, payload=None):
        self._status = status
        if self.status not in STATUS_STATES:
            raise ValueError("Status must be one of {}, but found {}".format(STATUS_STATES, self.status))
        self._message = message
        self._payload = payload

    @property
    def status(self):
        return self._status

    @property
    def message(self):
        return self._message

    @property
    def payload(self):
        return self._payload

    def ok(self):
        return self.status == SUCCESS

    def __str__(self):
        return "DKReturnCode {status: %s,\n message: %s,\n payload: %s}" % (
            self.status,
            self.message,
            self.payload,
        )

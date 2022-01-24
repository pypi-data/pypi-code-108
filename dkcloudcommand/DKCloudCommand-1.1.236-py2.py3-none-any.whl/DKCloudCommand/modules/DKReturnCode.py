from typing import Optional

from DKCommon.typing import JSONData


def convert_return_code(rc: "DKReturnCode") -> "DKReturnCode":
    # Convert new DKCommon return code into old DKReturnCode
    rc_old = DKReturnCode()
    rc_old.set(rc.status, rc.message, payload=rc.payload)
    return rc_old


# coalesce all errors from using the DataKitchen API into one simple structure
class DKReturnCode:
    DK_SUCCESS = "success"  # value
    DK_FAIL = "fail"  # value

    def __init__(self) -> None:
        self._status = None
        self._message = ""
        self._payload = None

    def set(self, status: str, message: str, payload: Optional[JSONData] = None) -> None:
        if status != self.DK_SUCCESS and status != self.DK_FAIL:
            raise ValueError(f"DKReturnCode.set() invalid value for status: {status}")
        self._status = status
        self.set_message(message)
        self._payload = payload

    def ok(self) -> bool:
        return self._status == self.DK_SUCCESS

    def get_message(self) -> str:
        return self._message

    def get_payload(self) -> JSONData:
        return self._payload

    def set_message(self, msg: Optional[str]) -> None:
        self._message = msg if msg is not None else ""

    def __str__(self) -> str:
        return f"DKReturnCode {{status: {self._status},\n message: {self._message},\n payload: {self._payload}}}"


# wrap the error returned from the DataKitchen API
# THIS CLASS COMPLETELY UNUSED?
class DKAPIReturnCode:
    def __init__(self, rdict, response=None):
        if isinstance(rdict, dict) is True and "message" in rdict:
            self.rd = rdict
        else:
            self.rd = None
        self.response = response

    # put all the logic here to dig out the error message from the API call
    def get_message(self):
        # got an rdict, look in there
        if self.rd is not None and isinstance(self.rd, dict):
            if "message" in self.rd:
                contents = self.rd["message"]
                if isinstance(contents, dict) and "error" in contents:
                    ret = contents["error"]
                    if "issues" in contents:
                        if contents["issues"] is not None:
                            for issue in contents["issues"]:
                                issueMessage = f'\n{issue["severity"]} - {issue["file"]} - {issue["description"]}'
                                ret += issueMessage
                    return ret
                elif isinstance(contents, str):
                    return contents
                else:
                    return "TODO: figure out this case"
        # no rdict, just have the HTTP response
        if self.response is not None:
            if isinstance(self.response.text, str):
                return self.response.text
        return ""


"""
The rdict varies.  Here are some examples

{
u'status': 500,
u'message': u'Internal Server Error'
}

{
  u'message': {
    u'error': u'unable to delete a branched-from-base-test-kitchen_ut_gil kitchen '
  }
}
"""

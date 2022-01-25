from requests import post
from requests.exceptions import RequestException

from smsit import Gateway, GatewayError
from warnings import warn


class NiksmsGateway(Gateway):
    """
    NikSMS

    Documentation:
        https://niksms.com/fa/main/امکانات-برنامه-نویسی-نیک-اس-ام-اس/Web-Service-API-چیست

    """

    _gateway_name = "niksms"
    _config_params = ("username", "password", "sender")
    _server_url = "https://niksms.com/fa/PublicApi"

    _send_status_map = {
        1: "Successful",
        2: "UnknownError",
        3: "InsufficientCredit",
        4: "ForbiddenHours",
        5: "Filtered",
        6: "NoFilters",
        7: "PrivateNumberIsDisable",
        8: "ArgumentIsNullOrIncorrect",
        9: "MessageBodyIsNullOrEmpty",
        10: "PrivateNumberIsIncorrect",
        11: "ReceptionNumberIsIncorrect",
        12: "SentTypeIsIncorrect",
        13: "Warning",
        14: "PanelIsBlocked",
        15: "SiteUpdating",
        16: "AudioMessageNotAllowed",
        17: "AudioMessageFileSizeNotAllowed",
        18: "PanelExpired",
        19: "InvalidUserNameOrPass",
    }

    def _call(self, path, params):
        try:
            resp = post(self._server_url + path, params=params)
            body = resp.json()
            code = int(body["Status"])
            if code != 1:
                reason = "%s-%s-%s" % (
                    code,
                    body["WarningMessage"],
                    self._send_status_map.get(code),
                )
                raise GatewayError(reason)

        except RequestException:
            raise GatewayError("Cannot send SMS")

        except Exception:
            raise GatewayError("Bad SMS gateway")

        return resp

    def send(self, message):
        params = {
            "Username": self.config["username"],
            "Password": self.config["password"],
            "Message": message.text,
            "Numbers": message.receiver,
            "SenderNumber": message.sender or self.config["sender"],
            "SendType": 1,  # 1: Normal | 2: Flash
        }

        if isinstance(message.meta, dict):
            params.update(message)

        return [self._call("/GroupSms", params)]

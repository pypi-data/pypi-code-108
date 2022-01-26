from requests import post
from requests.exceptions import RequestException

from smsit import Gateway, GatewayError


class GhasedakGateway(Gateway):
    """
    Ghasedak

    Documentation: https://ghasedak.me/docs

    """

    _gateway_name = "ghasedak"
    _config_params = ("apikey", "sender")
    _server_url = "https://api.ghasedak.me/v2/"

    _status_map = {
        1: "InvalidUserNameOrPass",
        2: "EmptyArray",
        3: "InvalidArrayLength",
        4: "SenderAndReceiverArrayMismatch",
        5: "CannotRecieveNewMessage",
        6: "DeactivatedAccount",
        7: "AccessForbidden",
        8: "InvalidReceiverNumber",
        9: "NotEnoughCredit",
        10: "InternalError",
        11: "InvalidIp",
        20: "ContactNumberFiltered",
        21: "CannotConnectToProvider",
        24: "CannotUseInFreePlan",
    }

    def _call(self, path, headers, params):
        try:
            resp = post(
                self._server_url + path,
                headers=headers,
                data=params,
            )
            body = resp.json()
            code = int(body["result"]["code"])
            if code != 200:
                reason = "%s-%s-%s" % (
                    code,
                    body["result"]["message"],
                    self._status_map.get(code),
                )
                raise GatewayError(reason)

        except RequestException:
            raise GatewayError("Cannot send message")

        except Exception:
            raise GatewayError("Bad gateway")

        return resp

    def send(self, message):
        headers = {
            "apikey": self.config["apikey"],
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
            "charset": "utf-8",
        }
        params = {"receptor": ",".join(message.receiver)}

        if isinstance(message.meta, dict):
            params.update(message.meta)

        if message.type == "sms":
            params["message"] = message.text
            sender = message.sender or self.config.get("sender")
            if sender:
                params["linenumber"] = sender

            return [self._call("/send/pair", headers, params)]

        if message.type == "templatedMessage":
            params["template"] = message.template
            for k, v in enumerate(message.params):
                params["param%s" % (k + 1)] = v

            return [self._call("/verification/send/simple", headers, params)]

        if message.type == "voiceMessage":
            params["message"] = message.text
            return [self._call("/voice/send/simple", headers, params)]

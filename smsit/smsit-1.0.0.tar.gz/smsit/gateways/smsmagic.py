from requests import post
from requests.exceptions import RequestException

from smsit import Gateway, GatewayError


class SmsmagicGateway(Gateway):
    """
    SMS-Magic

    Documentation: https://api.sms-magic.com/doc/#api-Send_SMS-Send_SMS___get

    Note: BulkSMS not working (returns 404)
    """

    _gateway_name = "sms_magic"
    _config_params = ("api_key", "sender_id")
    _server_url = "https://api.sms-magic.com/v1"

    def _call(self, path, headers, params):
        try:
            resp = post(self._server_url + path, headers=headers, json=params)
            code = resp.status_code
            if code != 200:
                raise GatewayError("Cannot send sms %s" % code)

        except RequestException:
            raise GatewayError("Cannot send SMS")

        return resp

    def send(self, message):
        headers = {
            "apikey": self.config["api_key"],
            "cache-control": "no-cache",
        }

        res = []
        for receiver in message.receiver:
            params = {
                "mobile_number": receiver,
                "sms_text": message.text,
                "sender_id": message.sender or self.config["sender_id"],
            }
            res.append(self._call("/sms/send", headers, params))

        return res

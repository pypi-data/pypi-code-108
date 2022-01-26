from smsit import Gateway


class DummyGateway(Gateway):  # pragma: nocover
    """
    Dummy Gateway

    """

    _gateway_name = "dummy"
    _config_params = ("api_key",)

    def send(self, sms):
        print("SMS Sent from dummy gateway, ", sms.__repr__())
        return True

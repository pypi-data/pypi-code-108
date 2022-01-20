import requests

from RainbowMonitoringSDK.exporters.Exporter import Exporter


class APIcallExporter(Exporter):
    """
    With this class the agent requests other service(s) at specific timestamps
    """

    def __init__(self, url: str,
                 method: str = "POST",
                 headers: dict = {},
                 auth: str = None,
                 password: str = None,
                 additional_params: dict = {}):
        self.url = url
        self.method = method
        self.headers = headers
        self.auth = auth
        self.password = password
        self.additional_params = additional_params

    def update(self, data: dict):
        try:
            data.update(self.additional_params)
            if self.method.lower() == 'get':
                res = self.__perform_get(data)
            elif self.method.lower() == 'post':
                res = self.__perform_post(data)
            else:
                res = self.__perform_other_methods(data)
            res.raise_for_status()
            return res
        except Exception as ex:
            print(ex)

    def __perform_get(self, data):
        return requests.get(
            self.url,
            auth=(self.auth, self.password) if self.auth and self.password else None,
            headers=self.headers,
            params=data
        )

    def __perform_post(self, data):
        return requests.post(
            self.url,
            auth=(self.auth, self.password) if self.auth and self.password else None,
            headers=self.headers,
            json=data
        )
    def __perform_other_methods(self, data):
        return getattr(requests, self.method.lower())(
            self.url,
            auth=(self.auth, self.password) if self.auth and self.password else None,
            headers=self.headers,
            json=data
        )

import requests


class NSession(requests.Session):
    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self.default_timeout = 60

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._session.close()

    def close(self):
        self._session.close()

    def get(self, url, **kwargs):

        if kwargs.get("timeout", None) is None:
            kwargs.update({"timeout": self.default_timeout})

        return self._session.get(url=url, **kwargs)

    def post(self, url, data=None, json: {}=None, **kwargs):
        """
        :param url:
        :param data:
        :param json: Dictionary object. Send your object using my_obj.__dict__
        :param kwargs:
        :return:
        """

        if kwargs.get("timeout", None) is None:
            kwargs.update({"timeout": self.default_timeout})

        return self._session.post(url=url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):

        if kwargs.get("timeout", None) is None:
            kwargs.update({"timeout": self.default_timeout})

        return self._session.delete(url=url, **kwargs)

    def put(self, url, data=None, **kwargs):

        if kwargs.get("timeout", None) is None:
            kwargs.update({"timeout": self.default_timeout})

        return self._session.put(url=url, data=data, **kwargs)

    def add_header(self, name, value):
        self._session.headers.update({name: value})

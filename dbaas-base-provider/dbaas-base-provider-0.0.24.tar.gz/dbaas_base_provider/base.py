from pymongo import MongoClient, ReturnDocument


class BaseProviderObject(object):
    _provider_type = None

    def __init__(self, *args, **kwargs):
        pass

    @property
    def provider_type(self):
        if self._provider_type:
            return self._provider_type
        raise NotImplementedError

    @provider_type.setter
    def provider_type(self, prov_type):
        self._provider_type = prov_type

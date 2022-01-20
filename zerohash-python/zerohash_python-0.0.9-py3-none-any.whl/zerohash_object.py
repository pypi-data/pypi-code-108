from zerohash import api_requestor, util


class ZerohashObject(dict):
    def __init__(self, id=None, credentials=None, **params):
        super().__init__()

        self._unsaved_values = set()
        self._transient_values = set()

        for k, v in params.items():
            self.__setattr__(k, v)

        self.__setattr__("credentials", credentials)
        if id:
            self["id"] = id

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            return super().__setattr__(k, v)
        self[k] = v
        return None

    def __getattr__(self, k):

        if k[0] == "_":
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as ke:
            raise AttributeError(*ke.args)

    @classmethod
    def construct_from(cls, values, credentials):
        instance = cls(values.get("id"), credentials=credentials)
        instance.refresh_from(values, credentials)
        return instance

    def request(self, method, url, params=None, headers=None):
        requestor = api_requestor.APIRequestor()
        response = requestor.request(method, url, params, headers)

        return util.convert_to_zerohash_object(response, credentials=self.credentials)

    def refresh_from(self, values, credentials=None, partial=False):
        self.credentials = credentials or getattr(values, "credentials", None)

        # TODO: conditional for if partial=True

        # Any values not set in values will be cleared/removed from the object returned after refresh
        removed = set(self.keys()) - set(values)
        self._transient_values = self._transient_values | removed
        self._unsaved_values = set()

        self.clear()

        self._transient_values = self._transient_values - set(values)

        for k, v in values.items():
            super().__setitem__(k, util.convert_to_zerohash_object(v, credentials))

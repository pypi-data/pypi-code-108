from ml.ml40.features.properties.values.value import Value


class FellingPeriod(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__from = None
        self.__to = None
        self.__json_out = dict()

    @property
    def _from(self):
        return self.__from

    @_from.setter
    def _from(self, value):
        self.__from = value

    @property
    def to(self):
        return self.__to

    @to.setter
    def to(self, value):
        self.__to = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self._from is not None:
            self.__json_out["from"] = self.__from
        if self.to is not None:
            self.__json_out["to"] = self.__to
        return self.__json_out

from ml.ml40.features.properties.values.value import Value


class Weight(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.__weight = None
        self.__json_out = {}

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        self.__weight = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.weight is not None:
            self.__json_out["weight"] = self.weight
        return self.__json_out

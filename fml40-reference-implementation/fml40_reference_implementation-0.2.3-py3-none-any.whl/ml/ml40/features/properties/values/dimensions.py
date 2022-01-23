from ml.ml40.features.properties.values.value import Value


class Dimensions(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.height = None
        self.length = None
        self.weight = None
        self.width = None
        self.__json_out = dict()

    def to_json(self):
        self.__json_out = super().to_json()
        if self.height is not None:
            self.__json_out["height"] = self.height
        if self.length is not None:
            self.__json_out["length"] = self.length
        if self.weight is not None:
            self.__json_out["weight"] = self.weight
        if self.width is not None:
            self.__json_out["width"] = self.width

        return self.__json_out

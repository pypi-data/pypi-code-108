from ml.ml40.features.properties.values.value import Value


class TreeType(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__conifer = None
        self.__json_out = dict()

    @property
    def conifer(self):
        return self.__conifer

    @conifer.setter
    def conifer(self, value):
        self.__conifer = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.conifer is not None:
            self.__json_out["conifer"] = self.conifer
        return self.__json_out

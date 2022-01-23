from ml.ml40.features.properties.values.value import Value


class InterferingBranches(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__exist = None
        self.__json_out = dict()

    @property
    def exist(self):
        return self.__exist

    @exist.setter
    def exist(self, value):
        self.__exist = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.exist is not None:
            self.__json_out["exist"] = self.__exist
        return self.__json_out

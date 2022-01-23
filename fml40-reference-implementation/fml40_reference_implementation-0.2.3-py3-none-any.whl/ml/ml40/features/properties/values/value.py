from ml.ml40.features.properties.property import Property


class Value(Property):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__valid_to = ""
        self.__valid_from = ""
        # TODO validate the datetype of valid from and valid to
        self.__json_out = {}

    @property
    def valid_to(self):
        return self.__valid_to

    @valid_to.setter
    def valid_to(self, value):
        self.__valid_to = value

    @property
    def valid_from(self):
        return self.__valid_from

    def valid_from(self, value):
        self.__valid_from = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.valid_from and self.valid_to:
            self.__json_out["valid_from"] = self.valid_from
            self.__json_out["valid_to"] = self.valid_to
        return self.__json_out

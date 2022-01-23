from ml.ml40.features.properties.values.value import Value


class PersonalName(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.firstname = None
        self.lastname = None
        self.__json_out = dict()

    def to_json(self):
        self.__json_out = super().to_json()
        if self.firstname is not None:
            self.__json_out["firstname"] = self.firstname

        if self.lastname is not None:
            self.__json_out["lastname"] = self.lastname

        return self.__json_out

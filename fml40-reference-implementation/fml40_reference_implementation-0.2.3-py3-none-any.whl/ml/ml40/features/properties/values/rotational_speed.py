from ml.ml40.features.properties.values.value import Value


class RotationalSpeed(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.__rpm = None
        self.__json_out = dict()

    @property
    def rpm(self):
        return self.__rpm

    @rpm.setter
    def rpm(self, value):
        self.__rpm = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.rpm is not None:
            self.__json_out["rpm"] = self.rpm
        return self.__json_out

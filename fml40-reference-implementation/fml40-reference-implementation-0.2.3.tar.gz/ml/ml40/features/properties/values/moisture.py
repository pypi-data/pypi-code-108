from ml.ml40.features.properties.values.value import Value


class Moisture(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__humidity = None
        self.__join_out = dict()

    @property
    def humidity(self):
        return self.__humidity

    @humidity.setter
    def humidity(self, value):
        self.__humidity = value

    def to_json(self):
        self.__join_out = super().to_json()
        if self.humidity is not None:
            self.__join_out["humidity"] = self.humidity
        return self.__join_out

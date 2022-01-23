from ml.ml40.features.properties.values.value import Value


class TimeSlot(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.end = None
        self.start = None
        self.__json_out = dict()

    def to_json(self):
        self.__json_out = super().to_json()
        if self.end is not None:
            self.__json_out["end"] = self.end
        if self.start is not None:
            self.__json_out["start"] = self.start
        return self.__json_out

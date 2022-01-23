from ml.ml40.features.properties.values.value import Value


class Tilt(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__direction = None
        self.__tilt = None
        self.__json_out = dict()

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        self.__direction = value

    @property
    def tilt(self):
        return self.__tilt

    @tilt.setter
    def tilt(self, value):
        self.__tilt = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.direction is not None:
            self.__json_out["direction"] = self.direction

        if self.tilt is not None:
            self.__json_out["tilt"] = self.tilt

        return self.__json_out

from ml.ml40.features.properties.values.value import Value


class OrientationRPY(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier,
            parent=parent
        )

        self.__roll = None
        self.__pitch = None
        self.__yaw = None
        self.__json_out = dict()

    @property
    def roll(self):
        return self.__roll

    @roll.setter
    def roll(self, value):
        self.__roll = value

    @property
    def pitch(self):
        return self.__pitch

    @pitch.setter
    def pitch(self, value):
        self.__pitch = value

    @property
    def yaw(self):
        return self.__yaw

    @yaw.setter
    def yaw(self, value):
        self.__yaw = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__roll is not None:
            self.__json_out["roll"] = self.__roll
        if self.__yaw is not None:
            self.__json_out["yaw"] = self.__yaw
        if self.__pitch is not None:
            self.__json_out["pitch"] = self.__pitch

        return self.__json_out


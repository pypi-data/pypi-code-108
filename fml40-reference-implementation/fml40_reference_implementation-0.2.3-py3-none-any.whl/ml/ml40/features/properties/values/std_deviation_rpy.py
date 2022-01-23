from ml.ml40.features.properties.values.value import Value


class StdDeviationRPY(Value):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier
        )

        self.__std_deviation_roll = None
        self.__std_deviation_pitch = None
        self.__std_deviation_yaw = None
        self.__json_out = {}

    @property
    def stdDeviationRoll(self):
        return self.__std_deviation_roll

    @stdDeviationRoll.setter
    def stdDeviationRoll(self, value):
        self.__std_deviation_roll = value

    @property
    def stdDeviationPitch(self):
        return self.__std_deviation_pitch

    @stdDeviationPitch.setter
    def stdDeviationPitch(self, value):
        self.__std_deviation_pitch = value

    @property
    def stdDeviationYaw(self):
        return self.__std_deviation_yaw

    @stdDeviationYaw.setter
    def stdDeviationYaw(self, value):
        self.__std_deviation_yaw = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__std_deviation_roll is not None:
            self.__json_out["stdDeviationRoll"] = self.__std_deviation_roll
        if self.__std_deviation_yaw is not None:
            self.__json_out["stdDeviationPitch"] = self.__std_deviation_yaw
        if self.__std_deviation_pitch is not None:
            self.__json_out["stdDeviationYaw"] = self.__std_deviation_pitch

        return self.__json_out


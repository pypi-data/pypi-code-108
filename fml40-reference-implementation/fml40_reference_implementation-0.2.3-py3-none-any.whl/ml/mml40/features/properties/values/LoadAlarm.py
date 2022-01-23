from ml.ml40.features.properties.values.value import Value


class LoadAlarm(Value):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)

        self.__is_alarm = None
        self.__displacement_threshold = None

    @property
    def isAlarm(self):
        return self.__is_alarm

    @isAlarm.setter
    def isAlarm(self, value):
        self.__is_alarm = value

    @property
    def displacementThreshold(self):
        return self.__displacement_threshold

    @displacementThreshold.setter
    def displacementThreshold(self, value):
        self.__displacement_threshold = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__is_alarm is not None:
            self.__json_out["isAlarm"] = self.__is_alarm
        if self.__displacement_threshold is not None:
            self.__json_out["displacementThreshold"] = self.__displacement_threshold

        return self.__json_out

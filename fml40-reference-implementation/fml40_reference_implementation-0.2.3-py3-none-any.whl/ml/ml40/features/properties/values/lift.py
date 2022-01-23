from ml.ml40.features.properties.values.value import Value


class Lift(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.__current_lift = None
        self.__max_lift = None
        self.__min_lift = None
        self.__json_out = dict()

    @property
    def currentLift(self):
        return self.__current_lift

    @currentLift.setter
    def currentLift(self, value):
        self.__current_lift = value

    @property
    def maxLift(self):
        return self.__max_lift

    @maxLift.setter
    def maxLift(self, value):
        self.__max_lift = value

    @property
    def minLift(self):
        return self.__min_lift

    @minLift.setter
    def minLift(self, value):
        self.__min_lift = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__current_lift is not None:
            self.__json_out["currentLift"] = self.__current_lift
        if self.__max_lift is not None:
            self.__json_out["maxLift"] = self.__max_lift
        if self.__min_lift is not None:
            self.__json_out["minLift"] = self.__min_lift

        return self.__json_out

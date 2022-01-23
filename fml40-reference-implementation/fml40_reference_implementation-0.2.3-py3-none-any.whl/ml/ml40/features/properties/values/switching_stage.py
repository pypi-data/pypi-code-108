from ml.ml40.features.properties.values.value import Value


class SwitchingStage(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.__min_stage = None
        self.__current_stage = None
        self.__max_stage = None
        self.__json_out = dict()

    @property
    def minStage(self):
        return self.__min_stage

    @minStage.setter
    def minStage(self, value):
        self.__min_stage = value

    @property
    def currentStage(self):
        return self.__current_stage

    @currentStage.setter
    def currentStage(self, value):
        self.__current_stage = value

    @property
    def maxStage(self):
        return self.__max_stage

    @maxStage.setter
    def maxStage(self, value):
        self.__max_stage = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.minStage is not None:
            self.__json_out["minStage"] = self.minStage
        if self.maxStage is not None:
            self.__json_out["maxStage"] = self.maxStage
        if self.currentStage is not None:
            self.__json_out["currentStage"] = self.currentStage
        return self.__json_out

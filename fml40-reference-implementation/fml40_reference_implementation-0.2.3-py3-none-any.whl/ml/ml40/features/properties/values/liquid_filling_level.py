from ml.ml40.features.properties.values.value import Value


class LiquidFillingLevel(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.currentLevel = None
        self.maxLevel = None
        self.__json_out = dict()

    def to_json(self):
        self.__json_out = super().to_json()
        if self.currentLevel is not None:
            self.__json_out["currentLevel"] = self.currentLevel
        if self.maxLevel is not None:
            self.__json_out["maxLevel"] = self.maxLevel
        return self.__json_out

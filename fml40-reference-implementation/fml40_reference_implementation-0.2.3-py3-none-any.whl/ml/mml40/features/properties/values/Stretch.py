from ml.ml40.features.properties.values.value import Value


class Stretch(Value):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)

        self.__stretch = None
        self.__min_stretch = None
        self.__max_stretch = None

    @property
    def stretch(self):
        return self.__stretch

    @stretch.setter
    def stretch(self, value):
        self.__stretch = value

    @property
    def minStretch(self):
        return self.__min_stretch

    @minStretch.setter
    def minStretch(self, value):
        self.__min_stretch = value

    @property
    def maxStretch(self):
        return self.__max_stretch

    @maxStretch.setter
    def maxStretch(self, value):
        self.__max_stretch = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__stretch is not None:
            self.__json_out["stretch"] = self.__stretch
        if self.__min_stretch is not None:
            self.__json_out["minStretch"] = self.__min_stretch
        if self.__max_stretch is not None:
            self.__json_out["maxStretch"] = self.__max_stretch
        return self.__json_out

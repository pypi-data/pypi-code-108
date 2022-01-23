from ml.ml40.features.properties.values.value import Value


class StemSegmentProperties(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(namespace=namespace, name=name, identifier=identifier, parent=parent)

        self.__diameter = None
        self.__length = None
        self.__quality = None
        self.__woodType = None
        self.__json_out = dict()

    @property
    def diameter(self):
        return self.__diameter

    @diameter.setter
    def diameter(self, value):
        self.__diameter = value

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value

    @property
    def quality(self):
        return self.__quality

    @quality.setter
    def quality(self, value):
        self.__quality = value

    @property
    def woodType(self):
        return self.__woodType

    @woodType.setter
    def woodType(self, value):
        self.__woodType = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.diameter is not None:
            self.__json_out["diameter"] = self.diameter

        if self.length is not None:
            self.__json_out["length"] = self.length

        if self.woodType is not None:
            self.__json_out["woodType"] = self.woodType

        if self.quality is not None:
            self.__json_out["quality"] = self.quality

        return self.__json_out

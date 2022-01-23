from ml.ml40.features.properties.values.value import Value


class Displacement(Value):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)
        self.__displacement = None
        self.__min_displacement = None
        self.__max_displacement = None
        self.__displacements = []

    @property
    def displacement(self):
        return self.__displacement

    @displacement.setter
    def displacement(self, value):
        self.__displacement = value

    @property
    def maxDisplacement(self):
        return self.__max_displacement

    @maxDisplacement.setter
    def maxDisplacement(self, value):
        self.__max_displacement = value

    @property
    def minDisplacement(self):
        return self.__min_displacement

    @minDisplacement.setter
    def minDisplacement(self, value):
        self.__min_displacement = value

    @property
    def displacements(self):
        return self.__displacements

    @displacements.setter
    def displacements(self, value):
        self.__displacements = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.displacement is not None:
            self.__json_out["displacement"] = self.__displacement
        if self.__min_displacement is not None:
            self.__json_out["minDisplacement"] = self.__min_displacement
        if self.__max_displacement is not None:
            self.__json_out["maxDisplacement"] = self.__max_displacement
        if self.__displacements:
            self.__json_out["displacements"] = self.__displacements
        return self.__json_out

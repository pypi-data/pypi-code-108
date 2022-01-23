from ml.ml40.features.properties.values.value import Value


class Force(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__force = None
        self.__min_force = None
        self.__max_force = None

    @property
    def force(self):
        return self.__force

    @force.setter
    def force(self, value):
        self.__force = value

    @property
    def minForce(self):
        return self.__min_force

    @minForce.setter
    def minForce(self, value):
        self.__min_force = value

    @property
    def maxForce(self):
        return self.__max_force

    @maxForce.setter
    def maxForce(self, value):
        self.__max_force = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__force is not None:
            self.__json_out["force"] = self.__force

        if self.__min_force is not None:
            self.__json_out["minForce"] = self.__min_force

        if self.__max_force is not None:
            self.__json_out["maxForce"] = self.__max_force

        return self.__json_out

from ml.ml40.features.properties.values.value import Value


class ExpansionLength(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

        self.__current_length = None
        self.__max_length = None
        self.__json_out = dict()

    @property
    def currentLength(self):
        return self.__current_length

    @currentLength.setter
    def currentLength(self, value):
        self.__current_length = value

    @property
    def maxLength(self):
        return self.__max_length

    @maxLength.setter
    def maxLength(self, value):
        self.__max_length = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__current_length is not None:
            self.__json_out["currentLength"] = self.__current_length
        if self.__max_length is not None:
            self.__json_out["maxLength"] = self.__max_length

        return self.__json_out

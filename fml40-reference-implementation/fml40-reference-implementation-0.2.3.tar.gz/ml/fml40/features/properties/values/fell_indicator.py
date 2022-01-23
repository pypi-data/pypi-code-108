from ml.ml40.features.properties.values.value import Value


class FellIndicator(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(namespace=namespace, name=name, identifier=identifier, parent=parent)
        self.__marked = None
        self.__json_out = dict()

    @property
    def marked(self):
        return self.__marked

    @marked.setter
    def marked(self, value):
        self.__marked = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.marked is not None:
            self.__json_out["marked"] = self.__marked
        return self.__json_out

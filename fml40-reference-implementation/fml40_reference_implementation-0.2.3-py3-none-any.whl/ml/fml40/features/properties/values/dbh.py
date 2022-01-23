from ml.ml40.features.properties.values.value import Value


class DBH(Value):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__dbh = None
        self.__json_out = dict()

    @property
    def dbh(self):
        return self.__dbh

    @dbh.setter
    def dbh(self, value):
        self.__dbh = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.dbh is not None:
            self.__json_out["dbh"] = self.dbh
        return self.__json_out

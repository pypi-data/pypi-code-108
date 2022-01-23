from ml.ml40.features.properties.values.value import Value


class Location(Value):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__latitude = None
        self.__longitude = None
        self.__orientation = None
        self.__json_out = {}

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        self.__latitude = value

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        self.__longitude = value

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.latitude is not None:
            self.__json_out["latitude"] = self.latitude
        if self.longitude is not None:
            self.__json_out["longitude"] = self.longitude
        if self.orientation is not None:
            self.__json_out["orientation"] = self.orientation
        return self.__json_out

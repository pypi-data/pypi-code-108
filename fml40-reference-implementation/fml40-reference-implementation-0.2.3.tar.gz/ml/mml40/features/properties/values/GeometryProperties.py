from ml.ml40.features.properties.values.value import Value


class GeometryProperties(Value):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)
        self.__geometry_type = None
        self.__length = None
        self.__width = None
        self.__height = None
        self.__thickness = None
        self.__json_out = dict()

    @property
    def geometryType(self):
        return self.__geometry_type

    @geometryType.setter
    def geometryType(self, value):
        self.__geometry_type = value

    @property
    def thickness(self):
        return self.__thickness

    @thickness.setter
    def thickness(self, value):
        self.__thickness = value

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__geometry_type is not None:
            self.__json_out["geometryType"] = self.__geometry_type

        if self.__length is not None:
            self.__json_out["length"] = self.__length

        if self.__width is not None:
            self.__json_out["width"] = self.__width

        if self.__height is not None:
            self.__json_out["height"] = self.__height

        if (
            self.__thickness is not None
            and self.__geometry_type == "rectangular_hollow_profile"
        ):
            self.__json_out["thickness"] = self.__thickness
        else:
            self.__json_out["thickness"] = ""

        return self.__json_out

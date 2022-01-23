from ml.ml40.features.properties.values.value import Value


class HighSpeedImageValue(Value):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier)

        self.__number_of_pixel = None
        self.__min_range = None
        self.__max_range = None

        self.__min_pixel_value = None
        self.__max_pixel_value = None

        self.__mean_pixel_value = None

    @property
    def numberOfPixel(self):
        return self.__number_of_pixel

    @numberOfPixel.setter
    def numberOfPixel(self, value):
        self.__number_of_pixel = value

    @property
    def minRange(self):
        return self.__min_range

    @minRange.setter
    def minRange(self, value):
        self.__min_range = value

    @property
    def maxPixelValue(self):
        return self.__max_pixel_value

    @maxPixelValue.setter
    def maxPixelValue(self, value):
        self.__max_pixel_value = value

    @property
    def minPixelValue(self):
        return self.__min_pixel_value

    @minPixelValue.setter
    def minPixelValue(self, value):
        self.__min_pixel_value = value

    @property
    def meanPixelValue(self):
        return self.__mean_pixel_value

    @meanPixelValue.setter
    def meanPixelValue(self, value):
        self.__mean_pixel_value = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__number_of_pixel is not None:
            self.__json_out["numberOfPixel"] = self.__number_of_pixel

        if self.__min_range is not None:
            self.__json_out["minRange"] = self.__min_range

        if self.__max_range is not None:
            self.__json_out["maxRange"] = self.__max_range

        if self.__min_pixel_value is not None:
            self.__json_out["minPixelValue"] = self.__min_pixel_value

        if self.__max_pixel_value is not None:
            self.__json_out["maxPixelValue"] = self.__max_pixel_value

        if self.__mean_pixel_value is not None:
            self.__json_out["meanPixelValue"] = self.__mean_pixel_value

        return self.__json_out


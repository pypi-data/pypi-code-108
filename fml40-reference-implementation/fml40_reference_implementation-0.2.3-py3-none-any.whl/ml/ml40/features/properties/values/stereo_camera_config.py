from ml.ml40.features.properties.values.value import Value


class StereoCameraConfig(Value):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier)

        self.__frame_rate = None
        self.__disparity_format = None

    @property
    def frameRate(self):
        return self.__frame_rate

    @frameRate.setter
    def frameRate(self, value):
        self.__frame_rate = value

    @property
    def disparityFormat(self):
        return self.__disparity_format

    @disparityFormat.setter
    def disparityFormat(self, value):
        self.__disparity_format = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__frame_rate is not None:
            self.__json_out["frameRate"] = self.__frame_rate
        if self.__disparity_format is not None:
            self.__json_out["disparityFormat"] = self.__disparity_format
        return self.__json_out
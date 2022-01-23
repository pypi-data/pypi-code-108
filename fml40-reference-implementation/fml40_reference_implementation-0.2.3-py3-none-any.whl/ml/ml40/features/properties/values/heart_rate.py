from ml.ml40.features.properties.values.value import Value


class HeartRate(Value):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier
        )
        self.__current_heart_rate = None
        self.__min_heart_rate = None
        self.__max_heart_rate = None
        self.__mean_heart_rate = None

    @property
    def currentHeartRate(self):
        return self.__current_heart_rate

    @currentHeartRate.setter
    def currentHeartRate(self, value):
        self.__current_heart_rate = value

    @property
    def minHeartRate(self):
        return self.__min_heart_rate

    @minHeartRate.setter
    def minHeartRate(self, value):
        self.__min_heart_rate = value

    @property
    def maxHeartRate(self):
        return self.__max_heart_rate

    @maxHeartRate.setter
    def maxHeartRate(self, value):
        self.__max_heart_rate = value

    @property
    def meanHeartRate(self):
        return self.__mean_heart_rate

    @meanHeartRate.setter
    def meanHeartRate(self, value):
        self.__mean_heart_rate = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__current_heart_rate is not None:
            self.__json_out["currentHeartRate"] = self.__current_heart_rate

        if self.__min_heart_rate is not None:
            self.__json_out["minHeartRate"] = self.__min_heart_rate

        if self.__max_heart_rate is not None:
            self.__json_out["maxHeartRate"] = self.__max_heart_rate

        if self.__mean_heart_rate is not None:
            self.__json_out["meanHeartRate"] = self.__mean_heart_rate

        return self.__json_out

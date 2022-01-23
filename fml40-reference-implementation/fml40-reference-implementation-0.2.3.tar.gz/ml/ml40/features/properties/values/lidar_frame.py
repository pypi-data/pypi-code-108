from ml.ml40.features.properties.values.value import Value


class LidarFrame(Value):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier)

        self.__no_scan_lines = None
        self.__no_points = None

    @property
    def noScanLines(self):
        return self.__no_scan_lines

    @noScanLines.setter
    def noScanLines(self, value):
        self.__no_scan_lines = value

    @property
    def noPoints(self):
        return self.__no_points

    @noPoints.setter
    def noPoints(self, value):
        self.__no_points = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.__no_scan_lines is not None:
            self.__json_out["noScanLines"] = self.__no_scan_lines
        if self.noPoints is not None:
            self.__json_out["noPoints"] = self.noPoints
        return self.__json_out

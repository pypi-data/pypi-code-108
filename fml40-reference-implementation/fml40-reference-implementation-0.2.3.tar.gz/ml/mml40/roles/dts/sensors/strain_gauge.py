from ml.ml40.roles.dts.sensors.sensor import Sensor


class StrainGauge(Sensor):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)

from ml.ml40.roles.dts.sensors.sensor import Sensor


class SoilSensor(Sensor):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(SoilSensor, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

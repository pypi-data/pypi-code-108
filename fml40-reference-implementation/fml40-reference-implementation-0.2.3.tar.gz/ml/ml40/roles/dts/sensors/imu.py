from ml.ml40.roles.dts.sensors.sensor import Sensor


class IMU(Sensor):
    """
    Inertia measurement unit
    """
    def __init__(self, namespace="ml40", name="", identifier=""):
        super(IMU, self).__init__(
            namespace=namespace, name=name, identifier=identifier
        )

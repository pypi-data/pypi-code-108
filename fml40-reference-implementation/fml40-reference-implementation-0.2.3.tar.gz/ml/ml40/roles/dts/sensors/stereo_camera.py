from ml.ml40.roles.dts.sensors.sensor import Sensor


class StereoCamera(Sensor):
    def __init__(self, namespace="ml40", name="", identifier=""):
        super(StereoCamera, self).__init__(
            namespace=namespace, name=name, identifier=identifier
        )

from ml.ml40.roles.dts.dt import DT


class Sensor(DT):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

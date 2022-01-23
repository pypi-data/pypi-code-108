from ml.ml40.roles.dts.dt import DT


class HandheldDevice(DT):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

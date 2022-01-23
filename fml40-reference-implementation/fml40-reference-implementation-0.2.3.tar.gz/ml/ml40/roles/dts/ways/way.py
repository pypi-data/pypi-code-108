from ml.ml40.roles.dts.dt import DT


class Way(DT):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Way, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

from ml.ml40.roles.dts.dt import DT


class Part(DT):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Part, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

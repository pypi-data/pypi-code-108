from ml.fml40.roles.dts.woods.wood import Wood


class StemSegment(Wood):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

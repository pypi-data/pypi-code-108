from ml.role import Role


class HMI(Role):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(HMI, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

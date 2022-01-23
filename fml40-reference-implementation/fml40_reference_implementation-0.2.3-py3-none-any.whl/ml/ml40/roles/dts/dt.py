from ml.role import Role


class DT(Role):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(namespace=namespace, name=name, identifier=identifier, parent=parent)

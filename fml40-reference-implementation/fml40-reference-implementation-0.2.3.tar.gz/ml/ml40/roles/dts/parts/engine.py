from ml.ml40.roles.dts.parts.part import Part


class Engine(Part):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Engine, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

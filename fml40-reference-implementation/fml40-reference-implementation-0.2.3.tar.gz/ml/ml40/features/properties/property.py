from ml.feature import Feature


class Property(Feature):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Property, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

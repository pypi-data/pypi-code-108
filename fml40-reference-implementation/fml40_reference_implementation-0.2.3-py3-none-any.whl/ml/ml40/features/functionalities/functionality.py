from ml.feature import Feature


class Functionality(Feature):
    """Genric implementation of a Functionaliy."""

    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super(Functionality, self).__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

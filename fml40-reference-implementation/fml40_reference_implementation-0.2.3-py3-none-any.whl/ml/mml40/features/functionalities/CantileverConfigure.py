from ml.ml40.features.functionalities.functionality import Functionality


class CantileverConfigure(Functionality):
    def __init__(self, namespace="mml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getConfiguration(self):
        pass

    def setConfiguration(self):
        pass

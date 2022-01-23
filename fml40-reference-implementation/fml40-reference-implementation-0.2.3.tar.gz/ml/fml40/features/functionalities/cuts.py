"""This module implements the class Cuts."""

from ml.ml40.features.functionalities.functionality import Functionality


class Cuts(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def cut(self):
        pass

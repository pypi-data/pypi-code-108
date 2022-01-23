"""This module implements the class GeneratesAfforestationSuggestions."""

from ml.identifier import ID
from ml.ml40.features.functionalities.functionality import Functionality


class GeneratesFellingSuggestions(Functionality):
    """This functionality can generate suggestions regarding how to fell a
    tree.
    """

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def generateFellingSuggestion(self, tree_Id: ID):
        """Returns a suggestion regarding how to fell a tree.

        :param: tree_Id: Identifier of a tree
        """
        pass

"""This module implements the class ForestPlanningEvaluation."""

from ml.ml40.features.functionalities.functionality import Functionality


class ForestPlanningEvaluation(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def evaluateInventoryData(self):
        pass

"""This module implements the class EvaluatesStandAttributes."""

from datetime import date

from ml.ml40.features.functionalities.functionality import Functionality


class EvaluatesStandAttributes(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def calculateStandAttributes(self, input_a: bytes, input_b: date) -> str:
        pass

    def calculateStock(self, input_a: bytes) -> float:
        pass

"""This module implements the class GeneratesAfforestationSuggestions."""

from ml.fml40.features.properties.values.documents.reports.afforestation_suggestion import (
    AfforestationSuggestion,
)
from ml.ml40.features.functionalities.functionality import Functionality


class GeneratesAfforestationSuggestions(Functionality):
    """This functionality can generate suggestions for afforestation."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def generateAfforestationSuggestion(self) -> AfforestationSuggestion:
        """Returns a suggestion for afforestation.

        :returns: Suggestion for afforestation
        :rtype: AfforestationSuggestion
        """
        pass

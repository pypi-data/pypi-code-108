"""This module implements the class AcceptsProximityAlert."""

from ml.ml40.features.functionalities.functionality import Functionality


class AcceptsProximityAlert(Functionality):
    """This functionality signalizes that an alert is generated if things
    are to close to this thing."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def proximityAlert(self, ids: list, distances: list):
        print("Making Proximity Alert...")

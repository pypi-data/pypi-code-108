from ml.ml40.features.functionalities.functionality import Functionality
from ml.mml40.features.properties.values.Displacement import Displacement


class ProvidesDisplacementData(Functionality):
    def __init__(self, namespace="mml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(namespace=namespace, name=name, identifier=identifier, parent=parent)

    def getMaxDisplacement(self) -> Displacement:
        pass

    def getMinDisplacement(self) -> Displacement:
        pass

    def getDisplacementData(self, time) -> [Displacement]:
        pass

    def getDisplacementDataSeries(self, startTime, endTime) -> [Displacement]:
        pass

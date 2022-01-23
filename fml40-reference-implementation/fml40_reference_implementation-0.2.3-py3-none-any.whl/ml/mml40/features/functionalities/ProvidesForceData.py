from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.force import Force


class ProvidesForceData(Functionality):
    def __init__(self, namespace="mml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getMaxForce(self) -> Force:
        pass

    def getMinForce(self) -> Force:
        pass

    def getForceData(self, time) -> Force:
        pass

    def getForceDataSeries(self, startTime, endTime) -> [Force]:
        pass

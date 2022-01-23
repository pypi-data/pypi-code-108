from ml.ml40.features.functionalities.functionality import Functionality
from ml.mml40.features.properties.values.Stretch import Stretch


class ProvidesStretchData(Functionality):
    def __init__(self, namespace="mml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getStretchData(self, time) -> Stretch:
        pass

    def getStretchDataSeries(self, startTime, endTime):
        pass

    def getMaxStretch(self) -> Stretch:
        pass

    def getMinStretch(self) -> Stretch:
        pass

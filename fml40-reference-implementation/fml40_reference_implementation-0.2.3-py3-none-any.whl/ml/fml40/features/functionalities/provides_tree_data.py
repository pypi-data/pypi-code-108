from ml.fml40.features.properties.values.tree_data import TreeData
from ml.identifier import ID
from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.location import Location


class ProvidesTreeData(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getTreeData(self, Tree: ID) -> list:
        pass

    def getTreesInDiameter(self, location: Location, diameter: float) -> list:
        pass

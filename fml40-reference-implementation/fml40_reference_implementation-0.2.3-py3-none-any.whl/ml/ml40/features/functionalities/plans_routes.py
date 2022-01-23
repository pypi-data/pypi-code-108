from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.location import Location
from ml.ml40.features.properties.values.route import Route


class PlansRoutes(Functionality):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def planRoute(self, start: Location, goal: Location) -> Route:
        pass

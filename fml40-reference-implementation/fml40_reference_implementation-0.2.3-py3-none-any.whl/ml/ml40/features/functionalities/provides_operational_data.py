from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.documents.reports.report import Report


class ProvidesOperationalData(Functionality):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getOperationalData(self) -> Report:
        return "this is a simply report"

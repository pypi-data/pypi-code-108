from ml.fml40.features.properties.values.documents.reports.passability_report import \
    PassabilityReport
from ml.ml40.features.functionalities.functionality import Functionality


class ProvidesMapData(Functionality):
    def __init__(self,namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier,
            parent=parent)

    def getMapData(self, map: int) -> PassabilityReport:
        pass

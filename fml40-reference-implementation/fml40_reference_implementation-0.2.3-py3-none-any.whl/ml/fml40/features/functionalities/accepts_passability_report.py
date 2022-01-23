from ml.fml40.features.properties.values.documents.reports.passability_report import (
    PassabilityReport,
)
from ml.ml40.features.functionalities.functionality import Functionality


class AcceptsPassabilityReport(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def acceptsReport(self, report: PassabilityReport):
        pass

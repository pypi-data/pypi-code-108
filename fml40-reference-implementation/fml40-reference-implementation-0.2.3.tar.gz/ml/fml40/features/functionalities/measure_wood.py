from ml.fml40.features.properties.values.documents.reports.log_measurement import (
    LogMeasurement,
)
from ml.ml40.features.functionalities.functionality import Functionality


class MeasuresWood(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def measureLog(self) -> LogMeasurement:
        pass

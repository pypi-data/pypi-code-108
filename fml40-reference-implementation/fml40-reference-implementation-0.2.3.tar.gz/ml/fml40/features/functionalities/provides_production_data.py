from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.documents.reports.production_data import (
    ProductionData,
)


class ProvidesProductionData(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def getProductionData(self) -> ProductionData:
        return "Production Data is huge"

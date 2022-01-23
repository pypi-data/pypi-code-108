from ml.ml40.features.properties.values.documents.reports.report import Report


class ProductionData(Report):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

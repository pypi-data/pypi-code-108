from ml.fml40.features.functionalities.converts_data_formats import ConvertsDataFormats


class ConvertsForestGML(ConvertsDataFormats):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

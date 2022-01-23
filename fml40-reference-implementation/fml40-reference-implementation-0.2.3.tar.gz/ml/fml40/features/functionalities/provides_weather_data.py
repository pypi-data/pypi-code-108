from ml.ml40.features.functionalities.functionality import Functionality


class ProvidesWeatherData(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

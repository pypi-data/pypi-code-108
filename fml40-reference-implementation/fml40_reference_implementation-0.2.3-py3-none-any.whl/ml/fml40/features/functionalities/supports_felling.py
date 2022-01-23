from ml.fml40.features.properties.values.documents.jobs.felling_job import FellingJob
from ml.ml40.features.functionalities.functionality import Functionality


class SupportsFelling(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def supportFelling(self, job: FellingJob, suggestion):
        pass

from ml.app_logger import APP_LOGGER
from ml.fml40.features.properties.values.documents.jobs.felling_job import FellingJob
from ml.ml40.features.functionalities.functionality import Functionality


class Harvests(Functionality):
    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier,
        )

    def executeJob(self, job: FellingJob):
        pass

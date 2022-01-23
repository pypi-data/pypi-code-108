from ml.identifier import ID
from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.documents.jobs.job import Job
from ml.ml40.features.properties.values.documents.reports.report import Report


class ManagesJobs(Functionality):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace,
            name=name,
            identifier=identifier,
            parent=parent)

    def acceptReport(self, report: Report):
        pass

    def assignJob(self, job: Job, identifier: ID):
        pass

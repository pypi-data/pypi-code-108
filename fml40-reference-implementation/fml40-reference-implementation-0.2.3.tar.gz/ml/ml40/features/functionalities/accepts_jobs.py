from ml.identifier import ID
from ml.ml40.features.functionalities.functionality import Functionality
from ml.ml40.features.properties.values.documents.jobs.job import Job
from ml.ml40.features.properties.values.documents.jobs.job_status import JobStatus


class AcceptsJobs(Functionality):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def acceptJob(self, job: Job) -> bool:
        pass

    def queryJobStatus(self, identifier: ID) -> JobStatus:
        pass

    def removeJob(self, identifier: ID) -> bool:
        pass

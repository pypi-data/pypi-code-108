from ml.ml40.features.properties.values.documents.document import Document
from ml.ml40.features.properties.values.documents.jobs.job_status import JobStatus


class Job(Document):
    def __init__(self, namespace="ml40", name="", identifier="", parent=None):
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )
        self.__status = None
        self.__json_out = dict()

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value: JobStatus):
        self.__status = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.status is not None:
            self.__json_out["status"] = self.status
        return self.__json_out

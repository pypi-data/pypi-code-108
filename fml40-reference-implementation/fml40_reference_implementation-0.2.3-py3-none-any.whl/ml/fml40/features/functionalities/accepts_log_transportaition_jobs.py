"""This module implements the class AcceptsLogTransportationJobs."""

from ml.fml40.features.properties.values.documents.jobs.log_transportation_job import (
    LogTransportationJob,
)
from ml.ml40.features.functionalities.accepts_jobs import AcceptsJobs


class AcceptsLogTransportationJobs(AcceptsJobs):
    """This functionality signalizes that LogTransportationJobs can be
    processed."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def acceptJob(self, job: LogTransportationJob) -> bool:
        """Accepts the given LogTransportationJob. Returns true if the job has
        been accepted, otherwise returns false.

        :param job: LogTransportationJob to be accepted
        :rtype: bool

        """
        pass

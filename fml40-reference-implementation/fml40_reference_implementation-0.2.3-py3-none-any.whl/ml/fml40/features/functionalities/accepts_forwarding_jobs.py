"""This module implements the class AcceptsForwardingJobs."""

from ml.app_logger import APP_LOGGER
from ml.fml40.features.properties.values.documents.jobs.forwarding_job import (
    ForwardingJob,
)
from ml.ml40.features.functionalities.accepts_jobs import AcceptsJobs


class AcceptsForwardingJobs(AcceptsJobs):
    """This functionality signalizes that ForwadingJobs can be processed."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def acceptJob(self, job: ForwardingJob) -> bool:
        """Accepts the given ForwardingJob. Returns true if the job has been
        accepted, otherwise returns false.

        :param job: ForwardingJob to be accepted
        :rtype: bool

        """
        pass

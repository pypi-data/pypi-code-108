"""This module implements the class Forwards."""

from ml.fml40.features.properties.values.documents.jobs.forwarding_job import (
    ForwardingJob,
)
from ml.ml40.features.functionalities.functionality import Functionality


class Forwards(Functionality):
    """This functionality signalizes that ForwardingJobs can be processed."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def executeJob(self, job):
        """Executes the given job.

        :param job: Job to be executed
        """
        pass

    def from_json(self, json_obj):
        """Initalizes this object from json_object.

        :param json_obj: JSON representation of this object
        """
        super().from_json(json_obj)

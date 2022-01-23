"""This module implements the class AcceptsSingleTreeFellingJobs."""

from ml.ml40.features.functionalities.accepts_jobs import AcceptsJobs


class AcceptsSingleTreeFellingJobs(AcceptsJobs):
    """This functionality signalizes that single trees can be felled."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

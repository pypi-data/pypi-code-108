from abc import abstractmethod, ABCMeta


class AbstractStore:
    """
    Abstract class for Backend Storage.
    This class defines the API interface for front ends to connect with various types of backends.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Empty constructor for now. This is deliberately not marked as abstract, else every
        derived class would be forced to create one.
        """
        pass

    @abstractmethod
    def lc_create_run(self,
                      artifact):
        """
        Create a run under the specified experiment ID

        :param artifact: see LcArtifact in proto/life_cycle.proto

        :return: The ID of the created Run object
        """
        pass

    def create_tag(self, run_id, tag):
        """
        Set a tag for the specified run

        :param run_id: String id for the run
        :param tag: see /entities/lc_run_tag.py
        """
        pass


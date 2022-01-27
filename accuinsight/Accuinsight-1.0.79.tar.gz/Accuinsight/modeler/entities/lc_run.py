from Accuinsight.modeler.entities._modeler_object import _ModelerObject
from Accuinsight.modeler.protos.life_cycle_pb2 import LcRunInfo as ProtoLcRunInfo


class Run(_ModelerObject):
    """
    Run object.
    """

    def __init__(self, run_id):
        self._run_id = run_id

    @property
    def run_id(self):
        """
        The run id that is returned by back-end server.

        """
        return self._run_id

    def to_proto(self):
        run = ProtoLcRunInfo()
        run.run_id = self.run_id
        return run

    @classmethod
    def from_proto(cls, proto):
        return cls(run_id=proto.run_id)



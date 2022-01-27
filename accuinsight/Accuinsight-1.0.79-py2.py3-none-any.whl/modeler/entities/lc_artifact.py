from Accuinsight.modeler.entities._modeler_object import _ModelerObject
from Accuinsight.modeler.protos.life_cycle_pb2 import LcArtifact as ProtoLcArtifact


class LcArtifact(_ModelerObject):
    """
    Parameter object.
    """

    def __init__(self, name, version):
        self._name = name
        self._version = version

    @property
    def name(self):
        """String name corresponding to the artifact."""
        return self._name

    @property
    def version(self):
        """String version of the artifact."""
        return self._version

    def to_proto(self):
        param = ProtoLcArtifact()
        param.name = self.name
        param.version = self.version
        return param

    @classmethod
    def from_proto(cls, proto):
        return cls(proto.name, proto.version)

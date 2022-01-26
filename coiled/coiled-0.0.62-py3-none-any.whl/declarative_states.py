from enum import Enum


class ClusterStateEnum(str, Enum):
    """
    Valid states for Clusters
    """

    pending = "pending"
    starting = "starting"
    scaling = "scaling"
    ready = "ready"
    stopping = "stopping"
    stopped = "stopped"
    error = "error"

    def awaiting_readiness(self):
        return self.value in ("pending", "starting", "scaling")

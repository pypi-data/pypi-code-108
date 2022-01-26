from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Failure_Modes(Consumer):
    """Inteface to Warranties Failure Modes resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/failure-modes")
    def list(
        self,
        failure_mode_level_1: Query(type=str) = None,
    ):
        """This call will return a list of level 2 failure modes for the specified level 1 failure mode."""
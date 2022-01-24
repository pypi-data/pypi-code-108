from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Machine_Logs(Consumer):
    """Inteface to machine logs resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("machines/logs")
    def list(
        self,
        machine_log_uid: Query(type=str) = None,
        machine_uid: Query(type=str) = None,
        model: Query(type=str) = None,
        serial: Query(type=str) = None,
    ):
        """This call will return log information for the specified criteria."""

    @returns.json
    @delete("machines/logs")
    def delete(self, uid: Query(type=str)):
        """This call will delete the log information for the specified uid."""

    @returns.json
    @json
    @post("machines/logs")
    def insert(self, machine_log: Body):
        """This call will create log information with the specified parameters."""

    @returns.json
    @json
    @patch("machines/logs")
    def update(self, log: Body):
        """This call will update the log information with the specified parameters."""
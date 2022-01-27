from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Telematics(Consumer):
    """Inteface to Telematics resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("machines/telematics")
    def list(
        self,
        uid: Query(type=str) = None,
        machine_uid: Query(type=str) = None,
    ):
        """This call will return telematics information for the specified criteria."""

    @returns.json
    @delete("machines/telematics")
    def delete(self, uid: Query(type=str)):
        """This call will delete the telematics information for the specified uid."""

    @returns.json
    @json
    @post("machines/telematics")
    def insert(self, telematics: Body):
        """This call will create telematics information with the specified parameters."""

    @returns.json
    @json
    @patch("machines/telematics")
    def update(self, telematics: Body):
        """This call will update the telematics information with the specified parameters."""
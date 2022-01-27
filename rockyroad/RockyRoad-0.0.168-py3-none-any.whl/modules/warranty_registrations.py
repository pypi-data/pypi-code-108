from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Warranty_Registrations(Consumer):
    """Inteface to warranty registrations resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/registrations")
    def list(
        self,
        warranty_registration_uid: Query(type=str) = None,
        machine_uid: Query(type=str) = None,
        model: Query(type=str) = None,
        serial: Query(type=str) = None,
        account: Query(type=str) = None,
        account_uid: Query(type=str) = None,
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @delete("warranties/registrations")
    def delete(self, uid: Query(type=str)):
        """This call will delete the warranty registration information for the specified uid."""

    @returns.json
    @json
    @post("warranties/registrations")
    def insert(self, warranty_registration: Body):
        """This call will create warranty registration information with the specified parameters."""

    @returns.json
    @json
    @patch("warranties/registrations")
    def update(self, warranty_registration: Body):
        """This call will update the warranty registration information with the specified parameters."""
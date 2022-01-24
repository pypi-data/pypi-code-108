from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Catalog(Consumer):
    """Inteface to Machine Catalog resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("machines/catalog")
    def list(self, machine_catalog_uid: Query(type=str) = None):
        """This call will return detailed machine catalog information for the id specified or all machine catalog information if uid is specified."""

    @returns.json
    @json
    @post("machines/catalog")
    def insert(self, new_machine_catalog: Body):
        """This call will create a Machine Catalog entry with the specified parameters."""

    @returns.json
    @delete("machines/catalog")
    def delete(self, machine_catalog_uid: Query(type=str)):
        """This call will delete the Machine Catalog entry for the specified Machine Catalog uid."""

    @returns.json
    @json
    @patch("machines/catalog")
    def update(self, machine_catalog: Body):
        """This call will update the Machine Catalog with the specified parameters."""
from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Rates(Consumer):
    """Inteface to Warranties Rates resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/rates")
    def list(
        self,
        uid: Query(type=str) = None,
        dealer_account: Query(type=str) = None,  # remove after no longer in use
        daaler_account_uid: Query(type=str) = None,  # remove after no longer in use
        dealer_branch_uid: Query(type=str) = None,
    ):
        """This call will return detailed waranty rate information for the specified criteria."""

    @returns.json
    @http_get("warranties/rates/{uid}")
    def get(self, uid: str):
        """This call will return detailed waranty rate information for the specified uid."""

    @delete("warranties/rates/{uid}")
    def delete(self, uid: str):
        """This call will delete the warranty rates for the specified uid."""

    @returns.json
    @json
    @post("warranties/rates")
    def insert(self, warrantyRates: Body):
        """This call will create warranty rates with the specified parameters."""

    @json
    @patch("warranties/rates/{uid}")
    def update(self, uid: str, warrantyRates: Body):
        """This call will update the warranty rates with the specified parameters."""
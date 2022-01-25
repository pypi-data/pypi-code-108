from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Apbs(Consumer):
    """Inteface to APBs resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def status(self):
        return self.__Status(self)

    def requests(self):
        return self.__Requests(self)

    @returns.json
    @http_get("apbs")
    def list(
        self,
        apb_uid: Query(type=int) = None,
        account: Query(type=str) = None,
        list_apbs_for_dealer_supported_accounts: Query(type=bool) = None,
        list_apbs_for_dealer_supported_machines: Query(type=bool) = None,
        brand: Query(type=str) = None,
        model: Query(type=str) = None,
        serial: Query(type=str) = None,
        branch_uid: Query(type=str) = None,
        dealer_code: Query(type=str) = None,
        dealer_uid: Query(type=str) = None,
        dealer_branch_uid: Query(type=str) = None,
    ):
        """This call will return detailed APB information for the apb or machine specified or all APBs if nothing is specified."""

    @returns.json
    @json
    @post("apbs")
    def insert(self, new_apb: Body):
        """This call will create an APB with the specified parameters."""

    @returns.json
    @delete("apbs")
    def delete(self, apb_uid: Query(type=str)):
        """This call will delete the APB for the specified APB uid."""

    @returns.json
    @json
    @patch("apbs")
    def update(self, apb: Body):
        """This call will update the APB with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Status(Consumer):
        """Inteface to APB Status resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("apbs/status")
        def list(self, apb_uid: Query(type=str) = None):
            """This call will return detailed APB status information for the specified APB uid."""

        @returns.json
        @delete("apbs/status")
        def delete(self, apb_status_uid: Query(type=str)):
            """This call will delete the APB Status for the specified APB uid and APB Status uid."""

        @returns.json
        @json
        @post("apbs/status")
        def insert(self, new_apb_status: Body):
            """This call will create an alert request with the specified parameters."""

        @returns.json
        @json
        @patch("apbs/status")
        def update(self, apb_status: Body):
            """This call will update the APB status with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Requests(Consumer):
        """Inteface to APB Request resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("apbs/requests")
        def list(self, uid: Query(type=str) = None):
            """This call will return detailed information for APB requests for the specified APB Request uid."""

        @returns.json
        @http_get("apbs/requests/{uid}")
        def get(self, uid: str):
            """This call will return detailed information for the specified APB request."""

        @returns.json
        @delete("apbs/requests")
        def delete(self, uid: Query(type=str)):
            """This call will delete the APB Request for the specified APB Request uid."""

        @returns.json
        @json
        @post("apbs/requests")
        def insert(self, new_apb_request: Body):
            """This call will create an APB request with the specified parameters."""

        @returns.json
        @json
        @patch("apbs/requests")
        def update(self, apb_request: Body):
            """This call will update the APB Request with the specified parameters."""
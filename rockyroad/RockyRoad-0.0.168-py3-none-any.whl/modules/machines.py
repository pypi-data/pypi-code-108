from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Machines(Consumer):
    """Inteface to machines resource for the RockyRoad API."""

    from .machine_catalog import Catalog
    from .util_data import UtilData
    from .telematics import Telematics
    from .machine_logs import Machine_Logs

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def utilData(self):
        return self.UtilData(self)

    def catalog(self):
        return self.Catalog(self)

    def models(self):
        return self.__Models(self)

    def product_types(self):
        return self.__Products(self)

    def serials(self):
        return self.__Serials(self)

    def telematics(self):
        return self.Telematics(self)

    def brands(self):
        return self.__Brands(self)

    def logs(self):
        return self.Machine_Logs(self)

    @returns.json
    @http_get("machines")
    def list(
        self,
        machine_uid: Query(type=str) = None,
        brand: Query(type=str) = None,
        model: Query(type=str) = None,
        serial: Query(type=str) = None,
        account: Query(type=str) = None,
        account_uid: Query(type=str) = None,
        owner_company_uid: Query(type=str) = None,
        dealer_company_uid: Query(type=str) = None,
        dealer_branch_uid: Query(type=str) = None,
        dealer_account: Query(type=str) = None,
        dealer_account_uid: Query(type=str) = None,
        dealer_code: Query(type=str) = None,
        branch_uid: Query(type=str) = None,
        include_util_data: Query(type=str) = None,
    ):
        """This call will return machine information for the machine or account specified or all machines if nothing is specified."""

    @returns.json
    @http_get("machines/{uid}")
    def get(
        self,
        uid: str,
    ):
        """This call will return machine information for the specified machine."""

    @returns.json
    @json
    @post("machines")
    def insert(self, new_machine: Body):
        """This call will create a machine with the specified parameters."""

    @delete("machines/{uid}")
    def delete(self, uid: str):
        """This call will delete the machine for the specified id."""

    @json
    @patch("machines/{uid}")
    def update(self, uid: str, machine: Body):
        """This call will update the machine with the specified parameters."""

    @returns.json
    @json
    @post("machines/assign-to-default-dealer")
    def assign_machines_to_default_dealer(
        self,
        customer_account: Query(type=str),
        ignore_machines_with_dealer: Query(type=bool) = None,
    ):
        """This call will set the supporting dealer for machines owned by the customer to the default dealer for the customer."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Models(Consumer):
        """Inteface to machine model resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/models")
        def list(
            self,
            baseOnly: Query(type=bool) = None,
            brand: Query(type=str) = None,
            productType: Query(type=str) = None,
        ):
            """This call will return machine models for the specified criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Brands(Consumer):
        """Inteface to machine brands resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/models/brands")
        def list(self, model: Query(type=str) = None):
            """This call will return brands for the specified models."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Products(Consumer):
        """Inteface to machine product-type resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/product-types")
        def list(self, brand: Query(type=str) = None):
            """This call will return machine product types for the specified criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Serials(Consumer):
        """Inteface to machine serial resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/models/serials")
        def list(
            self,
            model: Query(type=str) = None,
        ):
            """This call will return machine serials for the specified criteria."""

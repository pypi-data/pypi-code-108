from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Summaries(Consumer):
    """Inteface to Summaries resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def machineParts(self):
        return self.__Machine_Parts(self)

    def machineOwners(self):
        return self.__Machine_Owners(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Machine_Parts(Consumer):
        """Inteface to Machine Parts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("summaries/machine-parts")
        def list(
            self,
            machine_uid: Query(type=str) = None,
            brand: Query(type=str) = None,
            model: Query(type=str) = None,
            serial: Query(type=str) = None,
            account: Query(type=str) = None,
            account_uid: Query(type=str) = None,
            dealer_account: Query(type=str) = None,
            dealer_account_uid: Query(type=str) = None,
            dealer_uid: Query(type=str) = None,
            account_association_uid: Query(type=str) = None,
        ):
            """This call will return detailed summary information of machine parts for the specified search criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Machine_Owners(Consumer):
        """Inteface to Machine Owners resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("summaries/machine-owners")
        def list(
            self,
            model: Query(type=str) = None,
            serial: Query(type=str) = None,
            machine_uid: Query(type=str) = None,
            account: Query(type=str) = None,
            account_uid: Query(type=str) = None,
            dealer_account: Query(type=str) = None,
            dealer_account_uid: Query(type=str) = None,
            dealer_uid: Query(type=str) = None,
            account_association_uid: Query(type=str) = None,
            serial_range_start: Query(type=int) = None,
            serial_range_stop: Query(type=int) = 1_000_000,
        ):
            """This call will return detailed summary information of machine owners for the specified serial range and criteria."""
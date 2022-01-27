from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Parts(Consumer):
    """Inteface to Parts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def kits(self):
        return self.__Kits(self)

    @returns.json
    @http_get("parts")
    def list(
        self,
        uid: Query(type=int) = None,
        partNumber: Query(type=str) = None,
        partName: Query(type=str) = None,
        isKit: Query(type=bool) = None,
        isKitPart: Query(type=bool) = None,
    ):
        """This call will return detailed part information for the part(s) specified or all parts if nothing is specified."""

    @returns.json
    @json
    @post("parts")
    def insert(self, part: Body):
        """This call will create a part with the specified parameters."""

    @returns.json
    @delete("parts")
    def delete(self, uid: Query(type=str)):
        """This call will delete the part for the specified uid."""

    @returns.json
    @json
    @patch("parts")
    def update(self, part: Body):
        """This call will update the part with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Kits(Consumer):
        """Inteface to Kits resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("parts/kits")
        def list(
            self,
            uid: Query(type=str) = None,
            kitPartNumber: Query(type=str) = None,
            partNumber: Query(type=str) = None,
        ):
            """This call will return detailed kit line item information for the specified uid, kitPartNumber, or partNumber."""

        @returns.json
        @delete("parts/kits")
        def delete(self, uid: Query(type=str)):
            """This call will delete the kit line item for the specified uid."""

        @returns.json
        @json
        @post("parts/kits")
        def insert(self, kit: Body):
            """This call will create a kit line item with the specified parameters."""

        @returns.json
        @json
        @patch("parts/kits")
        def update(self, kit: Body):
            """This call will update the kit line item with the specified parameters."""
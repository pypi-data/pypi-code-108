from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class UtilData(Consumer):
    """Inteface to machine utildata resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)
        self._base_url = Resource._base_url

    def stats(self):
        return self.__Stats(self)

    @returns.json
    @http_get("machines/util-data")
    def list(self, brand: Query(type=str), time_period: Query(type=str)):
        """This call will return utilization data for the time period specified in the query parameter."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Stats(Consumer):
        """Inteface to utildata stats resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/util-data/stats")
        def list(self):
            """This call will return stats for the utildatastatus table."""
from .module_imports import *


class Alerts(object):
    """Inteface to alerts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url

    def requests(self):
        return self.__Requests(self)

    def reports(self):
        return self.__Reports(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Requests(Consumer):
        """Inteface to alert requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("alerts/requests")
        def list(self, creator_email: Query = None):
            """This call will return detailed alert request information for the creator's email specified or all alert requests if no email is specified."""

        @returns.json
        @json
        @post("alerts/requests")
        def insert(self, new_alert_request: Body):
            """This call will create an alert request with the specified parameters."""

        @returns.json
        @delete("alerts/requests")
        def delete(self, brand: Query(type=str), alert_request_id: Query(type=int)):
            """This call will delete the alert request for the specified brand and alert request id."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Reports(Consumer):
        """Inteface to alert reports resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("alerts/reports")
        def list(self, creator_email: Query = None):
            """This call will return detailed alert report information for the creator's email specified or all alert reports if no email is specified."""
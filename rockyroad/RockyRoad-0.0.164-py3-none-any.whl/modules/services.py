from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Services(Consumer):
    """Inteface to Services resource for the RockyRoad API."""

    from .service_reports import Service_Reports

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def maintenanceIntervals(self):
        return self.__Maintenance_Intervals(self)

    def emails(self):
        return self.__Emails(self)

    def templates(self):
        return self.__Templates(self)

    def serviceReports(self):
        return self.Service_Reports(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Maintenance_Intervals(Consumer):
        """Inteface to Maintenance Intervals resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("services/maintenance-intervals")
        def list(
            self,
            uid: Query(type=str) = None,
            hours: Query(type=int) = None,
            brand: Query(type=str) = None,
            model: Query(type=str) = None,
            serial: Query(type=str) = None,
        ):
            """This call will return detailed information for all maintenance intervals or for those for the specified uid, hours, or brand and model."""

        @returns.json
        @delete("services/maintenance-intervals")
        def delete(self, uid: Query(type=str)):
            """This call will delete the maintenance interval for the specified uid."""

        @returns.json
        @json
        @post("services/maintenance-intervals")
        def insert(self, maintenanceInterval: Body):
            """This call will create a maintenance interval with the specified parameters."""

        @returns.json
        @json
        @patch("services/maintenance-intervals")
        def update(self, maintenanceInterval: Body):
            """This call will update the maintenance interval with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Emails(Consumer):
        """Inteface to Warranty Emails resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @json
        @post("services/emails/reset-service-due-hours")
        def resetServiceDueHours(
            self, email_fields: Body, useLocalTemplate: Query(type=bool) = None
        ):
            """This call will create a service request email from a template with the specified parameters."""

        @json
        @post("services/emails")
        def create(
            self,
            email_template: Query(type=str),
            email_fields: Body,
            useLocalTemplate: Query(type=bool) = None,
        ):
            """This call will create a service request email from a template with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Templates(Consumer):
        """Inteface to Templates resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def emails(self):
            return self.__Emails(self)

        def documents(self):
            return self.__Documents(self)

        def pdfs(self):
            return self.__Pdfs(self)

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Emails(Consumer):
            """Inteface to Email Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/emails")
            def create(
                self,
                email_template: Query(type=str),
                email_fields: Body,
            ):
                """This call will create html email content from a template with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Documents(Consumer):
            """Inteface to Documents Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/documents")
            def create(
                self,
                document_template: Query(type=str),
                document_fields: Body,
            ):
                """This call will create html document content from a template with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Pdfs(Consumer):
            """Inteface to PDF Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/pdfs")
            def create(
                self,
                pdf_params: Body,
                document_template: Query(type=str) = None,
                include_page_numbers: Query(type=bool) = False,
                orientation: Query(type=str) = "portrait",
            ):
                """This call will create html document content from a template with the specified parameters."""
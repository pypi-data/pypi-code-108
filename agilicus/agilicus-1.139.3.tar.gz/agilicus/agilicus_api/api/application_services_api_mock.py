from unittest.mock import MagicMock

class ApplicationServicesApiMock:

    def __init__(self):
        self.mock_create_application_service = MagicMock()
        self.mock_create_application_service_token = MagicMock()
        self.mock_create_client_configuration = MagicMock()
        self.mock_create_desktop_resource = MagicMock()
        self.mock_create_file_share_service = MagicMock()
        self.mock_create_service_forwarder = MagicMock()
        self.mock_delete_application_service = MagicMock()
        self.mock_delete_desktop_resource = MagicMock()
        self.mock_delete_file_share_service = MagicMock()
        self.mock_delete_service_forwarder = MagicMock()
        self.mock_get_application_service = MagicMock()
        self.mock_get_application_service_usage_metrics = MagicMock()
        self.mock_get_desktop_resource = MagicMock()
        self.mock_get_file_share_service = MagicMock()
        self.mock_get_file_share_usage_metrics = MagicMock()
        self.mock_get_service_forwarder = MagicMock()
        self.mock_list_application_services = MagicMock()
        self.mock_list_desktop_resources = MagicMock()
        self.mock_list_file_share_services = MagicMock()
        self.mock_list_service_forwarders = MagicMock()
        self.mock_replace_application_service = MagicMock()
        self.mock_replace_desktop_resource = MagicMock()
        self.mock_replace_file_share_service = MagicMock()
        self.mock_replace_service_forwarder = MagicMock()

    def create_application_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_application_service with MagicMock.
        """
        return self.mock_create_application_service(self, *args, **kwargs)

    def create_application_service_token(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_application_service_token with MagicMock.
        """
        return self.mock_create_application_service_token(self, *args, **kwargs)

    def create_client_configuration(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_client_configuration with MagicMock.
        """
        return self.mock_create_client_configuration(self, *args, **kwargs)

    def create_desktop_resource(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_desktop_resource with MagicMock.
        """
        return self.mock_create_desktop_resource(self, *args, **kwargs)

    def create_file_share_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_file_share_service with MagicMock.
        """
        return self.mock_create_file_share_service(self, *args, **kwargs)

    def create_service_forwarder(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.create_service_forwarder with MagicMock.
        """
        return self.mock_create_service_forwarder(self, *args, **kwargs)

    def delete_application_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.delete_application_service with MagicMock.
        """
        return self.mock_delete_application_service(self, *args, **kwargs)

    def delete_desktop_resource(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.delete_desktop_resource with MagicMock.
        """
        return self.mock_delete_desktop_resource(self, *args, **kwargs)

    def delete_file_share_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.delete_file_share_service with MagicMock.
        """
        return self.mock_delete_file_share_service(self, *args, **kwargs)

    def delete_service_forwarder(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.delete_service_forwarder with MagicMock.
        """
        return self.mock_delete_service_forwarder(self, *args, **kwargs)

    def get_application_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_application_service with MagicMock.
        """
        return self.mock_get_application_service(self, *args, **kwargs)

    def get_application_service_usage_metrics(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_application_service_usage_metrics with MagicMock.
        """
        return self.mock_get_application_service_usage_metrics(self, *args, **kwargs)

    def get_desktop_resource(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_desktop_resource with MagicMock.
        """
        return self.mock_get_desktop_resource(self, *args, **kwargs)

    def get_file_share_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_file_share_service with MagicMock.
        """
        return self.mock_get_file_share_service(self, *args, **kwargs)

    def get_file_share_usage_metrics(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_file_share_usage_metrics with MagicMock.
        """
        return self.mock_get_file_share_usage_metrics(self, *args, **kwargs)

    def get_service_forwarder(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.get_service_forwarder with MagicMock.
        """
        return self.mock_get_service_forwarder(self, *args, **kwargs)

    def list_application_services(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.list_application_services with MagicMock.
        """
        return self.mock_list_application_services(self, *args, **kwargs)

    def list_desktop_resources(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.list_desktop_resources with MagicMock.
        """
        return self.mock_list_desktop_resources(self, *args, **kwargs)

    def list_file_share_services(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.list_file_share_services with MagicMock.
        """
        return self.mock_list_file_share_services(self, *args, **kwargs)

    def list_service_forwarders(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.list_service_forwarders with MagicMock.
        """
        return self.mock_list_service_forwarders(self, *args, **kwargs)

    def replace_application_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.replace_application_service with MagicMock.
        """
        return self.mock_replace_application_service(self, *args, **kwargs)

    def replace_desktop_resource(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.replace_desktop_resource with MagicMock.
        """
        return self.mock_replace_desktop_resource(self, *args, **kwargs)

    def replace_file_share_service(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.replace_file_share_service with MagicMock.
        """
        return self.mock_replace_file_share_service(self, *args, **kwargs)

    def replace_service_forwarder(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationServicesApi.replace_service_forwarder with MagicMock.
        """
        return self.mock_replace_service_forwarder(self, *args, **kwargs)


from unittest.mock import MagicMock

class ServicesApiMock:

    def __init__(self):
        self.mock_create_service = MagicMock()
        self.mock_delete_service = MagicMock()
        self.mock_get_service = MagicMock()
        self.mock_list_services = MagicMock()
        self.mock_replace_service = MagicMock()

    def create_service(self, *args, **kwargs):
        """
        This method mocks the original api ServicesApi.create_service with MagicMock.
        """
        return self.mock_create_service(self, *args, **kwargs)

    def delete_service(self, *args, **kwargs):
        """
        This method mocks the original api ServicesApi.delete_service with MagicMock.
        """
        return self.mock_delete_service(self, *args, **kwargs)

    def get_service(self, *args, **kwargs):
        """
        This method mocks the original api ServicesApi.get_service with MagicMock.
        """
        return self.mock_get_service(self, *args, **kwargs)

    def list_services(self, *args, **kwargs):
        """
        This method mocks the original api ServicesApi.list_services with MagicMock.
        """
        return self.mock_list_services(self, *args, **kwargs)

    def replace_service(self, *args, **kwargs):
        """
        This method mocks the original api ServicesApi.replace_service with MagicMock.
        """
        return self.mock_replace_service(self, *args, **kwargs)


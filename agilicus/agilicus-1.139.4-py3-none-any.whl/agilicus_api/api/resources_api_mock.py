from unittest.mock import MagicMock

class ResourcesApiMock:

    def __init__(self):
        self.mock_add_resource = MagicMock()
        self.mock_delete_resource = MagicMock()
        self.mock_get_resource = MagicMock()
        self.mock_list_resources = MagicMock()
        self.mock_replace_resource = MagicMock()

    def add_resource(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.add_resource with MagicMock.
        """
        return self.mock_add_resource(self, *args, **kwargs)

    def delete_resource(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.delete_resource with MagicMock.
        """
        return self.mock_delete_resource(self, *args, **kwargs)

    def get_resource(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.get_resource with MagicMock.
        """
        return self.mock_get_resource(self, *args, **kwargs)

    def list_resources(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.list_resources with MagicMock.
        """
        return self.mock_list_resources(self, *args, **kwargs)

    def replace_resource(self, *args, **kwargs):
        """
        This method mocks the original api ResourcesApi.replace_resource with MagicMock.
        """
        return self.mock_replace_resource(self, *args, **kwargs)


from unittest.mock import MagicMock

class LaunchersApiMock:

    def __init__(self):
        self.mock_create_launcher = MagicMock()
        self.mock_delete_launcher = MagicMock()
        self.mock_get_launcher = MagicMock()
        self.mock_list_launchers = MagicMock()
        self.mock_replace_launcher = MagicMock()

    def create_launcher(self, *args, **kwargs):
        """
        This method mocks the original api LaunchersApi.create_launcher with MagicMock.
        """
        return self.mock_create_launcher(self, *args, **kwargs)

    def delete_launcher(self, *args, **kwargs):
        """
        This method mocks the original api LaunchersApi.delete_launcher with MagicMock.
        """
        return self.mock_delete_launcher(self, *args, **kwargs)

    def get_launcher(self, *args, **kwargs):
        """
        This method mocks the original api LaunchersApi.get_launcher with MagicMock.
        """
        return self.mock_get_launcher(self, *args, **kwargs)

    def list_launchers(self, *args, **kwargs):
        """
        This method mocks the original api LaunchersApi.list_launchers with MagicMock.
        """
        return self.mock_list_launchers(self, *args, **kwargs)

    def replace_launcher(self, *args, **kwargs):
        """
        This method mocks the original api LaunchersApi.replace_launcher with MagicMock.
        """
        return self.mock_replace_launcher(self, *args, **kwargs)


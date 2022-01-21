from unittest.mock import MagicMock

class MetricsApiMock:

    def __init__(self):
        self.mock_list_active_users = MagicMock()
        self.mock_list_top_users = MagicMock()

    def list_active_users(self, *args, **kwargs):
        """
        This method mocks the original api MetricsApi.list_active_users with MagicMock.
        """
        return self.mock_list_active_users(self, *args, **kwargs)

    def list_top_users(self, *args, **kwargs):
        """
        This method mocks the original api MetricsApi.list_top_users with MagicMock.
        """
        return self.mock_list_top_users(self, *args, **kwargs)


from unittest.mock import MagicMock

class DiagnosticsApiMock:

    def __init__(self):
        self.mock_list_logs = MagicMock()

    def list_logs(self, *args, **kwargs):
        """
        This method mocks the original api DiagnosticsApi.list_logs with MagicMock.
        """
        return self.mock_list_logs(self, *args, **kwargs)


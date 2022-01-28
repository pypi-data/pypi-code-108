from unittest.mock import MagicMock

class WhoamiApiMock:

    def __init__(self):
        self.mock_create_whoami = MagicMock()

    def create_whoami(self, *args, **kwargs):
        """
        This method mocks the original api WhoamiApi.create_whoami with MagicMock.
        """
        return self.mock_create_whoami(self, *args, **kwargs)


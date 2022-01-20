from unittest.mock import MagicMock

class PolicyApiMock:

    def __init__(self):
        self.mock_get_challenge_decision = MagicMock()
        self.mock_get_enrollment_decision = MagicMock()
        self.mock_map_attributes = MagicMock()

    def get_challenge_decision(self, *args, **kwargs):
        """
        This method mocks the original api PolicyApi.get_challenge_decision with MagicMock.
        """
        return self.mock_get_challenge_decision(self, *args, **kwargs)

    def get_enrollment_decision(self, *args, **kwargs):
        """
        This method mocks the original api PolicyApi.get_enrollment_decision with MagicMock.
        """
        return self.mock_get_enrollment_decision(self, *args, **kwargs)

    def map_attributes(self, *args, **kwargs):
        """
        This method mocks the original api PolicyApi.map_attributes with MagicMock.
        """
        return self.mock_map_attributes(self, *args, **kwargs)


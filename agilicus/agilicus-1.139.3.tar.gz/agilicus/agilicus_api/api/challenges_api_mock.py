from unittest.mock import MagicMock

class ChallengesApiMock:

    def __init__(self):
        self.mock_create_challenge = MagicMock()
        self.mock_create_totp_enrollment = MagicMock()
        self.mock_create_webauthn_enrollment = MagicMock()
        self.mock_delete_challenge = MagicMock()
        self.mock_delete_totp_enrollment = MagicMock()
        self.mock_delete_webauthn_enrollment = MagicMock()
        self.mock_get_answer = MagicMock()
        self.mock_get_challenge = MagicMock()
        self.mock_get_totp_enrollment = MagicMock()
        self.mock_get_webauthn_enrollment = MagicMock()
        self.mock_list_totp_enrollment = MagicMock()
        self.mock_list_webauthn_enrollments = MagicMock()
        self.mock_replace_challenge = MagicMock()
        self.mock_update_totp_enrollment = MagicMock()
        self.mock_update_webauthn_enrollment = MagicMock()

    def create_challenge(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.create_challenge with MagicMock.
        """
        return self.mock_create_challenge(self, *args, **kwargs)

    def create_totp_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.create_totp_enrollment with MagicMock.
        """
        return self.mock_create_totp_enrollment(self, *args, **kwargs)

    def create_webauthn_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.create_webauthn_enrollment with MagicMock.
        """
        return self.mock_create_webauthn_enrollment(self, *args, **kwargs)

    def delete_challenge(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.delete_challenge with MagicMock.
        """
        return self.mock_delete_challenge(self, *args, **kwargs)

    def delete_totp_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.delete_totp_enrollment with MagicMock.
        """
        return self.mock_delete_totp_enrollment(self, *args, **kwargs)

    def delete_webauthn_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.delete_webauthn_enrollment with MagicMock.
        """
        return self.mock_delete_webauthn_enrollment(self, *args, **kwargs)

    def get_answer(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.get_answer with MagicMock.
        """
        return self.mock_get_answer(self, *args, **kwargs)

    def get_challenge(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.get_challenge with MagicMock.
        """
        return self.mock_get_challenge(self, *args, **kwargs)

    def get_totp_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.get_totp_enrollment with MagicMock.
        """
        return self.mock_get_totp_enrollment(self, *args, **kwargs)

    def get_webauthn_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.get_webauthn_enrollment with MagicMock.
        """
        return self.mock_get_webauthn_enrollment(self, *args, **kwargs)

    def list_totp_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.list_totp_enrollment with MagicMock.
        """
        return self.mock_list_totp_enrollment(self, *args, **kwargs)

    def list_webauthn_enrollments(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.list_webauthn_enrollments with MagicMock.
        """
        return self.mock_list_webauthn_enrollments(self, *args, **kwargs)

    def replace_challenge(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.replace_challenge with MagicMock.
        """
        return self.mock_replace_challenge(self, *args, **kwargs)

    def update_totp_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.update_totp_enrollment with MagicMock.
        """
        return self.mock_update_totp_enrollment(self, *args, **kwargs)

    def update_webauthn_enrollment(self, *args, **kwargs):
        """
        This method mocks the original api ChallengesApi.update_webauthn_enrollment with MagicMock.
        """
        return self.mock_update_webauthn_enrollment(self, *args, **kwargs)


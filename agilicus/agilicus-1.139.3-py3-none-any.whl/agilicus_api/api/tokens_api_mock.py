from unittest.mock import MagicMock

class TokensApiMock:

    def __init__(self):
        self.mock_create_api_key = MagicMock()
        self.mock_create_api_key_introspection = MagicMock()
        self.mock_create_authentication_document = MagicMock()
        self.mock_create_bulk_delete_session_task = MagicMock()
        self.mock_create_bulk_revoke_session_task = MagicMock()
        self.mock_create_bulk_revoke_token_task = MagicMock()
        self.mock_create_introspect_token = MagicMock()
        self.mock_create_introspect_token_all_sub_orgs = MagicMock()
        self.mock_create_reissued_token = MagicMock()
        self.mock_create_revoke_token_task = MagicMock()
        self.mock_create_session = MagicMock()
        self.mock_create_session_and_token = MagicMock()
        self.mock_create_token = MagicMock()
        self.mock_create_token_validation = MagicMock()
        self.mock_delete_api_key = MagicMock()
        self.mock_delete_authentication_document = MagicMock()
        self.mock_delete_session = MagicMock()
        self.mock_get_api_key = MagicMock()
        self.mock_get_authentication_document = MagicMock()
        self.mock_get_session = MagicMock()
        self.mock_list_api_keys = MagicMock()
        self.mock_list_authentication_documents = MagicMock()
        self.mock_list_sessions = MagicMock()
        self.mock_list_tokens = MagicMock()
        self.mock_replace_api_key = MagicMock()
        self.mock_replace_session = MagicMock()
        self.mock_validate_identity_assertion = MagicMock()

    def create_api_key(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_api_key with MagicMock.
        """
        return self.mock_create_api_key(self, *args, **kwargs)

    def create_api_key_introspection(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_api_key_introspection with MagicMock.
        """
        return self.mock_create_api_key_introspection(self, *args, **kwargs)

    def create_authentication_document(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_authentication_document with MagicMock.
        """
        return self.mock_create_authentication_document(self, *args, **kwargs)

    def create_bulk_delete_session_task(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_bulk_delete_session_task with MagicMock.
        """
        return self.mock_create_bulk_delete_session_task(self, *args, **kwargs)

    def create_bulk_revoke_session_task(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_bulk_revoke_session_task with MagicMock.
        """
        return self.mock_create_bulk_revoke_session_task(self, *args, **kwargs)

    def create_bulk_revoke_token_task(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_bulk_revoke_token_task with MagicMock.
        """
        return self.mock_create_bulk_revoke_token_task(self, *args, **kwargs)

    def create_introspect_token(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_introspect_token with MagicMock.
        """
        return self.mock_create_introspect_token(self, *args, **kwargs)

    def create_introspect_token_all_sub_orgs(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_introspect_token_all_sub_orgs with MagicMock.
        """
        return self.mock_create_introspect_token_all_sub_orgs(self, *args, **kwargs)

    def create_reissued_token(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_reissued_token with MagicMock.
        """
        return self.mock_create_reissued_token(self, *args, **kwargs)

    def create_revoke_token_task(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_revoke_token_task with MagicMock.
        """
        return self.mock_create_revoke_token_task(self, *args, **kwargs)

    def create_session(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_session with MagicMock.
        """
        return self.mock_create_session(self, *args, **kwargs)

    def create_session_and_token(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_session_and_token with MagicMock.
        """
        return self.mock_create_session_and_token(self, *args, **kwargs)

    def create_token(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_token with MagicMock.
        """
        return self.mock_create_token(self, *args, **kwargs)

    def create_token_validation(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.create_token_validation with MagicMock.
        """
        return self.mock_create_token_validation(self, *args, **kwargs)

    def delete_api_key(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.delete_api_key with MagicMock.
        """
        return self.mock_delete_api_key(self, *args, **kwargs)

    def delete_authentication_document(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.delete_authentication_document with MagicMock.
        """
        return self.mock_delete_authentication_document(self, *args, **kwargs)

    def delete_session(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.delete_session with MagicMock.
        """
        return self.mock_delete_session(self, *args, **kwargs)

    def get_api_key(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.get_api_key with MagicMock.
        """
        return self.mock_get_api_key(self, *args, **kwargs)

    def get_authentication_document(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.get_authentication_document with MagicMock.
        """
        return self.mock_get_authentication_document(self, *args, **kwargs)

    def get_session(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.get_session with MagicMock.
        """
        return self.mock_get_session(self, *args, **kwargs)

    def list_api_keys(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.list_api_keys with MagicMock.
        """
        return self.mock_list_api_keys(self, *args, **kwargs)

    def list_authentication_documents(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.list_authentication_documents with MagicMock.
        """
        return self.mock_list_authentication_documents(self, *args, **kwargs)

    def list_sessions(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.list_sessions with MagicMock.
        """
        return self.mock_list_sessions(self, *args, **kwargs)

    def list_tokens(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.list_tokens with MagicMock.
        """
        return self.mock_list_tokens(self, *args, **kwargs)

    def replace_api_key(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.replace_api_key with MagicMock.
        """
        return self.mock_replace_api_key(self, *args, **kwargs)

    def replace_session(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.replace_session with MagicMock.
        """
        return self.mock_replace_session(self, *args, **kwargs)

    def validate_identity_assertion(self, *args, **kwargs):
        """
        This method mocks the original api TokensApi.validate_identity_assertion with MagicMock.
        """
        return self.mock_validate_identity_assertion(self, *args, **kwargs)


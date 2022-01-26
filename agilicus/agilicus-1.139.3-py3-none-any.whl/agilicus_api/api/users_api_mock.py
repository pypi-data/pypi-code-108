from unittest.mock import MagicMock

class UsersApiMock:

    def __init__(self):
        self.mock_bulk_update_metadata = MagicMock()
        self.mock_create_challenge_method = MagicMock()
        self.mock_create_service_account = MagicMock()
        self.mock_create_upstream_user_identity = MagicMock()
        self.mock_create_user = MagicMock()
        self.mock_create_user_identity_update = MagicMock()
        self.mock_create_user_metadata = MagicMock()
        self.mock_create_user_request = MagicMock()
        self.mock_delete_challenge_method = MagicMock()
        self.mock_delete_service_account = MagicMock()
        self.mock_delete_upstream_user_identity = MagicMock()
        self.mock_delete_user = MagicMock()
        self.mock_delete_user_metadata = MagicMock()
        self.mock_delete_user_request = MagicMock()
        self.mock_get_challenge_method = MagicMock()
        self.mock_get_service_account = MagicMock()
        self.mock_get_upstream_user_identity = MagicMock()
        self.mock_get_user = MagicMock()
        self.mock_get_user_metadata = MagicMock()
        self.mock_get_user_request = MagicMock()
        self.mock_list_access_requests = MagicMock()
        self.mock_list_all_resource_permissions = MagicMock()
        self.mock_list_all_user_orgs = MagicMock()
        self.mock_list_all_user_roles = MagicMock()
        self.mock_list_challenge_methods = MagicMock()
        self.mock_list_combined_user_details = MagicMock()
        self.mock_list_org_user_roles = MagicMock()
        self.mock_list_service_accounts = MagicMock()
        self.mock_list_upstream_user_identities = MagicMock()
        self.mock_list_user_application_access_info = MagicMock()
        self.mock_list_user_file_share_access_info = MagicMock()
        self.mock_list_user_guids = MagicMock()
        self.mock_list_user_launcher_access_info = MagicMock()
        self.mock_list_user_metadata = MagicMock()
        self.mock_list_user_permissions = MagicMock()
        self.mock_list_user_requests = MagicMock()
        self.mock_list_user_resource_access_info = MagicMock()
        self.mock_list_users = MagicMock()
        self.mock_replace_challenge_method = MagicMock()
        self.mock_replace_service_account = MagicMock()
        self.mock_replace_upstream_user_identity = MagicMock()
        self.mock_replace_user = MagicMock()
        self.mock_replace_user_metadata = MagicMock()
        self.mock_replace_user_request = MagicMock()
        self.mock_replace_user_role = MagicMock()
        self.mock_reset_user_mfa_challenge_methods = MagicMock()
        self.mock_update_user_request = MagicMock()

    def bulk_update_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.bulk_update_metadata with MagicMock.
        """
        return self.mock_bulk_update_metadata(self, *args, **kwargs)

    def create_challenge_method(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_challenge_method with MagicMock.
        """
        return self.mock_create_challenge_method(self, *args, **kwargs)

    def create_service_account(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_service_account with MagicMock.
        """
        return self.mock_create_service_account(self, *args, **kwargs)

    def create_upstream_user_identity(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_upstream_user_identity with MagicMock.
        """
        return self.mock_create_upstream_user_identity(self, *args, **kwargs)

    def create_user(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_user with MagicMock.
        """
        return self.mock_create_user(self, *args, **kwargs)

    def create_user_identity_update(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_user_identity_update with MagicMock.
        """
        return self.mock_create_user_identity_update(self, *args, **kwargs)

    def create_user_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_user_metadata with MagicMock.
        """
        return self.mock_create_user_metadata(self, *args, **kwargs)

    def create_user_request(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.create_user_request with MagicMock.
        """
        return self.mock_create_user_request(self, *args, **kwargs)

    def delete_challenge_method(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_challenge_method with MagicMock.
        """
        return self.mock_delete_challenge_method(self, *args, **kwargs)

    def delete_service_account(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_service_account with MagicMock.
        """
        return self.mock_delete_service_account(self, *args, **kwargs)

    def delete_upstream_user_identity(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_upstream_user_identity with MagicMock.
        """
        return self.mock_delete_upstream_user_identity(self, *args, **kwargs)

    def delete_user(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_user with MagicMock.
        """
        return self.mock_delete_user(self, *args, **kwargs)

    def delete_user_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_user_metadata with MagicMock.
        """
        return self.mock_delete_user_metadata(self, *args, **kwargs)

    def delete_user_request(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.delete_user_request with MagicMock.
        """
        return self.mock_delete_user_request(self, *args, **kwargs)

    def get_challenge_method(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_challenge_method with MagicMock.
        """
        return self.mock_get_challenge_method(self, *args, **kwargs)

    def get_service_account(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_service_account with MagicMock.
        """
        return self.mock_get_service_account(self, *args, **kwargs)

    def get_upstream_user_identity(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_upstream_user_identity with MagicMock.
        """
        return self.mock_get_upstream_user_identity(self, *args, **kwargs)

    def get_user(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_user with MagicMock.
        """
        return self.mock_get_user(self, *args, **kwargs)

    def get_user_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_user_metadata with MagicMock.
        """
        return self.mock_get_user_metadata(self, *args, **kwargs)

    def get_user_request(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.get_user_request with MagicMock.
        """
        return self.mock_get_user_request(self, *args, **kwargs)

    def list_access_requests(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_access_requests with MagicMock.
        """
        return self.mock_list_access_requests(self, *args, **kwargs)

    def list_all_resource_permissions(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_all_resource_permissions with MagicMock.
        """
        return self.mock_list_all_resource_permissions(self, *args, **kwargs)

    def list_all_user_orgs(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_all_user_orgs with MagicMock.
        """
        return self.mock_list_all_user_orgs(self, *args, **kwargs)

    def list_all_user_roles(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_all_user_roles with MagicMock.
        """
        return self.mock_list_all_user_roles(self, *args, **kwargs)

    def list_challenge_methods(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_challenge_methods with MagicMock.
        """
        return self.mock_list_challenge_methods(self, *args, **kwargs)

    def list_combined_user_details(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_combined_user_details with MagicMock.
        """
        return self.mock_list_combined_user_details(self, *args, **kwargs)

    def list_org_user_roles(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_org_user_roles with MagicMock.
        """
        return self.mock_list_org_user_roles(self, *args, **kwargs)

    def list_service_accounts(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_service_accounts with MagicMock.
        """
        return self.mock_list_service_accounts(self, *args, **kwargs)

    def list_upstream_user_identities(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_upstream_user_identities with MagicMock.
        """
        return self.mock_list_upstream_user_identities(self, *args, **kwargs)

    def list_user_application_access_info(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_application_access_info with MagicMock.
        """
        return self.mock_list_user_application_access_info(self, *args, **kwargs)

    def list_user_file_share_access_info(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_file_share_access_info with MagicMock.
        """
        return self.mock_list_user_file_share_access_info(self, *args, **kwargs)

    def list_user_guids(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_guids with MagicMock.
        """
        return self.mock_list_user_guids(self, *args, **kwargs)

    def list_user_launcher_access_info(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_launcher_access_info with MagicMock.
        """
        return self.mock_list_user_launcher_access_info(self, *args, **kwargs)

    def list_user_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_metadata with MagicMock.
        """
        return self.mock_list_user_metadata(self, *args, **kwargs)

    def list_user_permissions(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_permissions with MagicMock.
        """
        return self.mock_list_user_permissions(self, *args, **kwargs)

    def list_user_requests(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_requests with MagicMock.
        """
        return self.mock_list_user_requests(self, *args, **kwargs)

    def list_user_resource_access_info(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_user_resource_access_info with MagicMock.
        """
        return self.mock_list_user_resource_access_info(self, *args, **kwargs)

    def list_users(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.list_users with MagicMock.
        """
        return self.mock_list_users(self, *args, **kwargs)

    def replace_challenge_method(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_challenge_method with MagicMock.
        """
        return self.mock_replace_challenge_method(self, *args, **kwargs)

    def replace_service_account(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_service_account with MagicMock.
        """
        return self.mock_replace_service_account(self, *args, **kwargs)

    def replace_upstream_user_identity(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_upstream_user_identity with MagicMock.
        """
        return self.mock_replace_upstream_user_identity(self, *args, **kwargs)

    def replace_user(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_user with MagicMock.
        """
        return self.mock_replace_user(self, *args, **kwargs)

    def replace_user_metadata(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_user_metadata with MagicMock.
        """
        return self.mock_replace_user_metadata(self, *args, **kwargs)

    def replace_user_request(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_user_request with MagicMock.
        """
        return self.mock_replace_user_request(self, *args, **kwargs)

    def replace_user_role(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.replace_user_role with MagicMock.
        """
        return self.mock_replace_user_role(self, *args, **kwargs)

    def reset_user_mfa_challenge_methods(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.reset_user_mfa_challenge_methods with MagicMock.
        """
        return self.mock_reset_user_mfa_challenge_methods(self, *args, **kwargs)

    def update_user_request(self, *args, **kwargs):
        """
        This method mocks the original api UsersApi.update_user_request with MagicMock.
        """
        return self.mock_update_user_request(self, *args, **kwargs)


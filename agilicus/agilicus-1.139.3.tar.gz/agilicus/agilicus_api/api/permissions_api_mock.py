from unittest.mock import MagicMock

class PermissionsApiMock:

    def __init__(self):
        self.mock_bulk_delete_resource_permission = MagicMock()
        self.mock_create_resource_permission = MagicMock()
        self.mock_create_resource_role = MagicMock()
        self.mock_delete_resource_permission = MagicMock()
        self.mock_delete_resource_role = MagicMock()
        self.mock_get_elevated_user_roles = MagicMock()
        self.mock_get_resource_permission = MagicMock()
        self.mock_get_resource_role = MagicMock()
        self.mock_list_elevated_user_roles = MagicMock()
        self.mock_list_resource_permissions = MagicMock()
        self.mock_list_resource_roles = MagicMock()
        self.mock_list_resource_roles_for_type = MagicMock()
        self.mock_replace_elevated_user_role = MagicMock()
        self.mock_replace_resource_permission = MagicMock()
        self.mock_replace_resource_role = MagicMock()

    def bulk_delete_resource_permission(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.bulk_delete_resource_permission with MagicMock.
        """
        return self.mock_bulk_delete_resource_permission(self, *args, **kwargs)

    def create_resource_permission(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.create_resource_permission with MagicMock.
        """
        return self.mock_create_resource_permission(self, *args, **kwargs)

    def create_resource_role(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.create_resource_role with MagicMock.
        """
        return self.mock_create_resource_role(self, *args, **kwargs)

    def delete_resource_permission(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.delete_resource_permission with MagicMock.
        """
        return self.mock_delete_resource_permission(self, *args, **kwargs)

    def delete_resource_role(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.delete_resource_role with MagicMock.
        """
        return self.mock_delete_resource_role(self, *args, **kwargs)

    def get_elevated_user_roles(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.get_elevated_user_roles with MagicMock.
        """
        return self.mock_get_elevated_user_roles(self, *args, **kwargs)

    def get_resource_permission(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.get_resource_permission with MagicMock.
        """
        return self.mock_get_resource_permission(self, *args, **kwargs)

    def get_resource_role(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.get_resource_role with MagicMock.
        """
        return self.mock_get_resource_role(self, *args, **kwargs)

    def list_elevated_user_roles(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.list_elevated_user_roles with MagicMock.
        """
        return self.mock_list_elevated_user_roles(self, *args, **kwargs)

    def list_resource_permissions(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.list_resource_permissions with MagicMock.
        """
        return self.mock_list_resource_permissions(self, *args, **kwargs)

    def list_resource_roles(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.list_resource_roles with MagicMock.
        """
        return self.mock_list_resource_roles(self, *args, **kwargs)

    def list_resource_roles_for_type(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.list_resource_roles_for_type with MagicMock.
        """
        return self.mock_list_resource_roles_for_type(self, *args, **kwargs)

    def replace_elevated_user_role(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.replace_elevated_user_role with MagicMock.
        """
        return self.mock_replace_elevated_user_role(self, *args, **kwargs)

    def replace_resource_permission(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.replace_resource_permission with MagicMock.
        """
        return self.mock_replace_resource_permission(self, *args, **kwargs)

    def replace_resource_role(self, *args, **kwargs):
        """
        This method mocks the original api PermissionsApi.replace_resource_role with MagicMock.
        """
        return self.mock_replace_resource_role(self, *args, **kwargs)


from unittest.mock import MagicMock

class GroupsApiMock:

    def __init__(self):
        self.mock_add_group_member = MagicMock()
        self.mock_create_group = MagicMock()
        self.mock_create_upstream_group_reconcile = MagicMock()
        self.mock_create_upstream_group_reconcile_sim = MagicMock()
        self.mock_delete_group = MagicMock()
        self.mock_delete_group_member = MagicMock()
        self.mock_get_group = MagicMock()
        self.mock_list_groups = MagicMock()
        self.mock_replace_group = MagicMock()

    def add_group_member(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.add_group_member with MagicMock.
        """
        return self.mock_add_group_member(self, *args, **kwargs)

    def create_group(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.create_group with MagicMock.
        """
        return self.mock_create_group(self, *args, **kwargs)

    def create_upstream_group_reconcile(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.create_upstream_group_reconcile with MagicMock.
        """
        return self.mock_create_upstream_group_reconcile(self, *args, **kwargs)

    def create_upstream_group_reconcile_sim(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.create_upstream_group_reconcile_sim with MagicMock.
        """
        return self.mock_create_upstream_group_reconcile_sim(self, *args, **kwargs)

    def delete_group(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.delete_group with MagicMock.
        """
        return self.mock_delete_group(self, *args, **kwargs)

    def delete_group_member(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.delete_group_member with MagicMock.
        """
        return self.mock_delete_group_member(self, *args, **kwargs)

    def get_group(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.get_group with MagicMock.
        """
        return self.mock_get_group(self, *args, **kwargs)

    def list_groups(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.list_groups with MagicMock.
        """
        return self.mock_list_groups(self, *args, **kwargs)

    def replace_group(self, *args, **kwargs):
        """
        This method mocks the original api GroupsApi.replace_group with MagicMock.
        """
        return self.mock_replace_group(self, *args, **kwargs)


from unittest.mock import MagicMock

class OrganisationsApiMock:

    def __init__(self):
        self.mock_create_billing_portal_link = MagicMock()
        self.mock_create_blocking_upgrade_orgs_task = MagicMock()
        self.mock_create_org = MagicMock()
        self.mock_create_sub_org = MagicMock()
        self.mock_delete_sub_org = MagicMock()
        self.mock_get_org = MagicMock()
        self.mock_get_org_billing_account = MagicMock()
        self.mock_get_org_status = MagicMock()
        self.mock_get_usage_metrics = MagicMock()
        self.mock_list_orgs = MagicMock()
        self.mock_list_sub_orgs = MagicMock()
        self.mock_replace_org = MagicMock()

    def create_billing_portal_link(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.create_billing_portal_link with MagicMock.
        """
        return self.mock_create_billing_portal_link(self, *args, **kwargs)

    def create_blocking_upgrade_orgs_task(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.create_blocking_upgrade_orgs_task with MagicMock.
        """
        return self.mock_create_blocking_upgrade_orgs_task(self, *args, **kwargs)

    def create_org(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.create_org with MagicMock.
        """
        return self.mock_create_org(self, *args, **kwargs)

    def create_sub_org(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.create_sub_org with MagicMock.
        """
        return self.mock_create_sub_org(self, *args, **kwargs)

    def delete_sub_org(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.delete_sub_org with MagicMock.
        """
        return self.mock_delete_sub_org(self, *args, **kwargs)

    def get_org(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.get_org with MagicMock.
        """
        return self.mock_get_org(self, *args, **kwargs)

    def get_org_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.get_org_billing_account with MagicMock.
        """
        return self.mock_get_org_billing_account(self, *args, **kwargs)

    def get_org_status(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.get_org_status with MagicMock.
        """
        return self.mock_get_org_status(self, *args, **kwargs)

    def get_usage_metrics(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.get_usage_metrics with MagicMock.
        """
        return self.mock_get_usage_metrics(self, *args, **kwargs)

    def list_orgs(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.list_orgs with MagicMock.
        """
        return self.mock_list_orgs(self, *args, **kwargs)

    def list_sub_orgs(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.list_sub_orgs with MagicMock.
        """
        return self.mock_list_sub_orgs(self, *args, **kwargs)

    def replace_org(self, *args, **kwargs):
        """
        This method mocks the original api OrganisationsApi.replace_org with MagicMock.
        """
        return self.mock_replace_org(self, *args, **kwargs)


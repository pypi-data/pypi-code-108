from unittest.mock import MagicMock

class BillingApiMock:

    def __init__(self):
        self.mock_add_billing_usage_record = MagicMock()
        self.mock_add_org_to_billing_account = MagicMock()
        self.mock_create_billing_account = MagicMock()
        self.mock_create_product = MagicMock()
        self.mock_delete_billing_account = MagicMock()
        self.mock_delete_product = MagicMock()
        self.mock_get_billing_account = MagicMock()
        self.mock_get_billing_account_orgs = MagicMock()
        self.mock_get_product = MagicMock()
        self.mock_get_usage_records = MagicMock()
        self.mock_list_billing_accounts = MagicMock()
        self.mock_list_products = MagicMock()
        self.mock_remove_org_from_billing_account = MagicMock()
        self.mock_replace_billing_account = MagicMock()
        self.mock_replace_product = MagicMock()

    def add_billing_usage_record(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.add_billing_usage_record with MagicMock.
        """
        return self.mock_add_billing_usage_record(self, *args, **kwargs)

    def add_org_to_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.add_org_to_billing_account with MagicMock.
        """
        return self.mock_add_org_to_billing_account(self, *args, **kwargs)

    def create_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.create_billing_account with MagicMock.
        """
        return self.mock_create_billing_account(self, *args, **kwargs)

    def create_product(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.create_product with MagicMock.
        """
        return self.mock_create_product(self, *args, **kwargs)

    def delete_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.delete_billing_account with MagicMock.
        """
        return self.mock_delete_billing_account(self, *args, **kwargs)

    def delete_product(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.delete_product with MagicMock.
        """
        return self.mock_delete_product(self, *args, **kwargs)

    def get_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.get_billing_account with MagicMock.
        """
        return self.mock_get_billing_account(self, *args, **kwargs)

    def get_billing_account_orgs(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.get_billing_account_orgs with MagicMock.
        """
        return self.mock_get_billing_account_orgs(self, *args, **kwargs)

    def get_product(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.get_product with MagicMock.
        """
        return self.mock_get_product(self, *args, **kwargs)

    def get_usage_records(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.get_usage_records with MagicMock.
        """
        return self.mock_get_usage_records(self, *args, **kwargs)

    def list_billing_accounts(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.list_billing_accounts with MagicMock.
        """
        return self.mock_list_billing_accounts(self, *args, **kwargs)

    def list_products(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.list_products with MagicMock.
        """
        return self.mock_list_products(self, *args, **kwargs)

    def remove_org_from_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.remove_org_from_billing_account with MagicMock.
        """
        return self.mock_remove_org_from_billing_account(self, *args, **kwargs)

    def replace_billing_account(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.replace_billing_account with MagicMock.
        """
        return self.mock_replace_billing_account(self, *args, **kwargs)

    def replace_product(self, *args, **kwargs):
        """
        This method mocks the original api BillingApi.replace_product with MagicMock.
        """
        return self.mock_replace_product(self, *args, **kwargs)


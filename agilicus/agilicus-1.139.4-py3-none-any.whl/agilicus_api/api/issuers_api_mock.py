from unittest.mock import MagicMock

class IssuersApiMock:

    def __init__(self):
        self.mock_create_client = MagicMock()
        self.mock_create_issuer = MagicMock()
        self.mock_create_policy = MagicMock()
        self.mock_create_policy_rule = MagicMock()
        self.mock_create_upstream_alias = MagicMock()
        self.mock_create_upstream_group_mapping = MagicMock()
        self.mock_delete_client = MagicMock()
        self.mock_delete_policy = MagicMock()
        self.mock_delete_policy_rule = MagicMock()
        self.mock_delete_root = MagicMock()
        self.mock_delete_upstream_alias = MagicMock()
        self.mock_delete_upstream_group_mapping = MagicMock()
        self.mock_get_client = MagicMock()
        self.mock_get_issuer = MagicMock()
        self.mock_get_policy = MagicMock()
        self.mock_get_policy_rule = MagicMock()
        self.mock_get_root = MagicMock()
        self.mock_get_upstream_alias = MagicMock()
        self.mock_get_upstream_group_mapping = MagicMock()
        self.mock_get_upstreams = MagicMock()
        self.mock_get_wellknown_issuer_info = MagicMock()
        self.mock_list_clients = MagicMock()
        self.mock_list_issuer_roots = MagicMock()
        self.mock_list_issuer_upstreams = MagicMock()
        self.mock_list_issuers = MagicMock()
        self.mock_list_policies = MagicMock()
        self.mock_list_policy_rules = MagicMock()
        self.mock_list_upstream_aliases = MagicMock()
        self.mock_list_upstream_group_mappings = MagicMock()
        self.mock_list_wellknown_issuer_info = MagicMock()
        self.mock_replace_client = MagicMock()
        self.mock_replace_issuer = MagicMock()
        self.mock_replace_policy = MagicMock()
        self.mock_replace_policy_rule = MagicMock()
        self.mock_replace_root = MagicMock()
        self.mock_replace_upstream_alias = MagicMock()
        self.mock_replace_upstream_group_mapping = MagicMock()
        self.mock_reset_service_account = MagicMock()
        self.mock_reset_to_default_policy = MagicMock()
        self.mock_set_policy = MagicMock()

    def create_client(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_client with MagicMock.
        """
        return self.mock_create_client(self, *args, **kwargs)

    def create_issuer(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_issuer with MagicMock.
        """
        return self.mock_create_issuer(self, *args, **kwargs)

    def create_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_policy with MagicMock.
        """
        return self.mock_create_policy(self, *args, **kwargs)

    def create_policy_rule(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_policy_rule with MagicMock.
        """
        return self.mock_create_policy_rule(self, *args, **kwargs)

    def create_upstream_alias(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_upstream_alias with MagicMock.
        """
        return self.mock_create_upstream_alias(self, *args, **kwargs)

    def create_upstream_group_mapping(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.create_upstream_group_mapping with MagicMock.
        """
        return self.mock_create_upstream_group_mapping(self, *args, **kwargs)

    def delete_client(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_client with MagicMock.
        """
        return self.mock_delete_client(self, *args, **kwargs)

    def delete_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_policy with MagicMock.
        """
        return self.mock_delete_policy(self, *args, **kwargs)

    def delete_policy_rule(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_policy_rule with MagicMock.
        """
        return self.mock_delete_policy_rule(self, *args, **kwargs)

    def delete_root(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_root with MagicMock.
        """
        return self.mock_delete_root(self, *args, **kwargs)

    def delete_upstream_alias(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_upstream_alias with MagicMock.
        """
        return self.mock_delete_upstream_alias(self, *args, **kwargs)

    def delete_upstream_group_mapping(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.delete_upstream_group_mapping with MagicMock.
        """
        return self.mock_delete_upstream_group_mapping(self, *args, **kwargs)

    def get_client(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_client with MagicMock.
        """
        return self.mock_get_client(self, *args, **kwargs)

    def get_issuer(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_issuer with MagicMock.
        """
        return self.mock_get_issuer(self, *args, **kwargs)

    def get_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_policy with MagicMock.
        """
        return self.mock_get_policy(self, *args, **kwargs)

    def get_policy_rule(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_policy_rule with MagicMock.
        """
        return self.mock_get_policy_rule(self, *args, **kwargs)

    def get_root(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_root with MagicMock.
        """
        return self.mock_get_root(self, *args, **kwargs)

    def get_upstream_alias(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_upstream_alias with MagicMock.
        """
        return self.mock_get_upstream_alias(self, *args, **kwargs)

    def get_upstream_group_mapping(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_upstream_group_mapping with MagicMock.
        """
        return self.mock_get_upstream_group_mapping(self, *args, **kwargs)

    def get_upstreams(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_upstreams with MagicMock.
        """
        return self.mock_get_upstreams(self, *args, **kwargs)

    def get_wellknown_issuer_info(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.get_wellknown_issuer_info with MagicMock.
        """
        return self.mock_get_wellknown_issuer_info(self, *args, **kwargs)

    def list_clients(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_clients with MagicMock.
        """
        return self.mock_list_clients(self, *args, **kwargs)

    def list_issuer_roots(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_issuer_roots with MagicMock.
        """
        return self.mock_list_issuer_roots(self, *args, **kwargs)

    def list_issuer_upstreams(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_issuer_upstreams with MagicMock.
        """
        return self.mock_list_issuer_upstreams(self, *args, **kwargs)

    def list_issuers(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_issuers with MagicMock.
        """
        return self.mock_list_issuers(self, *args, **kwargs)

    def list_policies(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_policies with MagicMock.
        """
        return self.mock_list_policies(self, *args, **kwargs)

    def list_policy_rules(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_policy_rules with MagicMock.
        """
        return self.mock_list_policy_rules(self, *args, **kwargs)

    def list_upstream_aliases(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_upstream_aliases with MagicMock.
        """
        return self.mock_list_upstream_aliases(self, *args, **kwargs)

    def list_upstream_group_mappings(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_upstream_group_mappings with MagicMock.
        """
        return self.mock_list_upstream_group_mappings(self, *args, **kwargs)

    def list_wellknown_issuer_info(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.list_wellknown_issuer_info with MagicMock.
        """
        return self.mock_list_wellknown_issuer_info(self, *args, **kwargs)

    def replace_client(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_client with MagicMock.
        """
        return self.mock_replace_client(self, *args, **kwargs)

    def replace_issuer(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_issuer with MagicMock.
        """
        return self.mock_replace_issuer(self, *args, **kwargs)

    def replace_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_policy with MagicMock.
        """
        return self.mock_replace_policy(self, *args, **kwargs)

    def replace_policy_rule(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_policy_rule with MagicMock.
        """
        return self.mock_replace_policy_rule(self, *args, **kwargs)

    def replace_root(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_root with MagicMock.
        """
        return self.mock_replace_root(self, *args, **kwargs)

    def replace_upstream_alias(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_upstream_alias with MagicMock.
        """
        return self.mock_replace_upstream_alias(self, *args, **kwargs)

    def replace_upstream_group_mapping(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.replace_upstream_group_mapping with MagicMock.
        """
        return self.mock_replace_upstream_group_mapping(self, *args, **kwargs)

    def reset_service_account(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.reset_service_account with MagicMock.
        """
        return self.mock_reset_service_account(self, *args, **kwargs)

    def reset_to_default_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.reset_to_default_policy with MagicMock.
        """
        return self.mock_reset_to_default_policy(self, *args, **kwargs)

    def set_policy(self, *args, **kwargs):
        """
        This method mocks the original api IssuersApi.set_policy with MagicMock.
        """
        return self.mock_set_policy(self, *args, **kwargs)


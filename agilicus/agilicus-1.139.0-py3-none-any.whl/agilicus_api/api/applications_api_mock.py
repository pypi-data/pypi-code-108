from unittest.mock import MagicMock

class ApplicationsApiMock:

    def __init__(self):
        self.mock_add_config = MagicMock()
        self.mock_add_role = MagicMock()
        self.mock_add_role_to_rule_entry = MagicMock()
        self.mock_add_rule = MagicMock()
        self.mock_create_agent = MagicMock()
        self.mock_create_application = MagicMock()
        self.mock_delete_agent = MagicMock()
        self.mock_delete_application = MagicMock()
        self.mock_delete_config = MagicMock()
        self.mock_delete_role = MagicMock()
        self.mock_delete_role_to_rule_entry = MagicMock()
        self.mock_delete_rule = MagicMock()
        self.mock_get_agent = MagicMock()
        self.mock_get_all_usage_metrics = MagicMock()
        self.mock_get_application = MagicMock()
        self.mock_get_application_usage_metrics = MagicMock()
        self.mock_get_config = MagicMock()
        self.mock_get_environment = MagicMock()
        self.mock_get_role = MagicMock()
        self.mock_get_role_to_rule_entry = MagicMock()
        self.mock_get_rule = MagicMock()
        self.mock_list_agents = MagicMock()
        self.mock_list_application_summaries = MagicMock()
        self.mock_list_applications = MagicMock()
        self.mock_list_combined_rules = MagicMock()
        self.mock_list_configs = MagicMock()
        self.mock_list_environment_configs_all_apps = MagicMock()
        self.mock_list_role_to_rule_entries = MagicMock()
        self.mock_list_roles = MagicMock()
        self.mock_list_rules = MagicMock()
        self.mock_list_runtime_status = MagicMock()
        self.mock_replace_agent = MagicMock()
        self.mock_replace_application = MagicMock()
        self.mock_replace_config = MagicMock()
        self.mock_replace_environment = MagicMock()
        self.mock_replace_role = MagicMock()
        self.mock_replace_role_to_rule_entry = MagicMock()
        self.mock_replace_rule = MagicMock()
        self.mock_replace_runtime_status = MagicMock()
        self.mock_update_patch_application = MagicMock()

    def add_config(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.add_config with MagicMock.
        """
        return self.mock_add_config(self, *args, **kwargs)

    def add_role(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.add_role with MagicMock.
        """
        return self.mock_add_role(self, *args, **kwargs)

    def add_role_to_rule_entry(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.add_role_to_rule_entry with MagicMock.
        """
        return self.mock_add_role_to_rule_entry(self, *args, **kwargs)

    def add_rule(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.add_rule with MagicMock.
        """
        return self.mock_add_rule(self, *args, **kwargs)

    def create_agent(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.create_agent with MagicMock.
        """
        return self.mock_create_agent(self, *args, **kwargs)

    def create_application(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.create_application with MagicMock.
        """
        return self.mock_create_application(self, *args, **kwargs)

    def delete_agent(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_agent with MagicMock.
        """
        return self.mock_delete_agent(self, *args, **kwargs)

    def delete_application(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_application with MagicMock.
        """
        return self.mock_delete_application(self, *args, **kwargs)

    def delete_config(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_config with MagicMock.
        """
        return self.mock_delete_config(self, *args, **kwargs)

    def delete_role(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_role with MagicMock.
        """
        return self.mock_delete_role(self, *args, **kwargs)

    def delete_role_to_rule_entry(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_role_to_rule_entry with MagicMock.
        """
        return self.mock_delete_role_to_rule_entry(self, *args, **kwargs)

    def delete_rule(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.delete_rule with MagicMock.
        """
        return self.mock_delete_rule(self, *args, **kwargs)

    def get_agent(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_agent with MagicMock.
        """
        return self.mock_get_agent(self, *args, **kwargs)

    def get_all_usage_metrics(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_all_usage_metrics with MagicMock.
        """
        return self.mock_get_all_usage_metrics(self, *args, **kwargs)

    def get_application(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_application with MagicMock.
        """
        return self.mock_get_application(self, *args, **kwargs)

    def get_application_usage_metrics(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_application_usage_metrics with MagicMock.
        """
        return self.mock_get_application_usage_metrics(self, *args, **kwargs)

    def get_config(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_config with MagicMock.
        """
        return self.mock_get_config(self, *args, **kwargs)

    def get_environment(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_environment with MagicMock.
        """
        return self.mock_get_environment(self, *args, **kwargs)

    def get_role(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_role with MagicMock.
        """
        return self.mock_get_role(self, *args, **kwargs)

    def get_role_to_rule_entry(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_role_to_rule_entry with MagicMock.
        """
        return self.mock_get_role_to_rule_entry(self, *args, **kwargs)

    def get_rule(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.get_rule with MagicMock.
        """
        return self.mock_get_rule(self, *args, **kwargs)

    def list_agents(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_agents with MagicMock.
        """
        return self.mock_list_agents(self, *args, **kwargs)

    def list_application_summaries(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_application_summaries with MagicMock.
        """
        return self.mock_list_application_summaries(self, *args, **kwargs)

    def list_applications(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_applications with MagicMock.
        """
        return self.mock_list_applications(self, *args, **kwargs)

    def list_combined_rules(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_combined_rules with MagicMock.
        """
        return self.mock_list_combined_rules(self, *args, **kwargs)

    def list_configs(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_configs with MagicMock.
        """
        return self.mock_list_configs(self, *args, **kwargs)

    def list_environment_configs_all_apps(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_environment_configs_all_apps with MagicMock.
        """
        return self.mock_list_environment_configs_all_apps(self, *args, **kwargs)

    def list_role_to_rule_entries(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_role_to_rule_entries with MagicMock.
        """
        return self.mock_list_role_to_rule_entries(self, *args, **kwargs)

    def list_roles(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_roles with MagicMock.
        """
        return self.mock_list_roles(self, *args, **kwargs)

    def list_rules(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_rules with MagicMock.
        """
        return self.mock_list_rules(self, *args, **kwargs)

    def list_runtime_status(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.list_runtime_status with MagicMock.
        """
        return self.mock_list_runtime_status(self, *args, **kwargs)

    def replace_agent(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_agent with MagicMock.
        """
        return self.mock_replace_agent(self, *args, **kwargs)

    def replace_application(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_application with MagicMock.
        """
        return self.mock_replace_application(self, *args, **kwargs)

    def replace_config(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_config with MagicMock.
        """
        return self.mock_replace_config(self, *args, **kwargs)

    def replace_environment(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_environment with MagicMock.
        """
        return self.mock_replace_environment(self, *args, **kwargs)

    def replace_role(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_role with MagicMock.
        """
        return self.mock_replace_role(self, *args, **kwargs)

    def replace_role_to_rule_entry(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_role_to_rule_entry with MagicMock.
        """
        return self.mock_replace_role_to_rule_entry(self, *args, **kwargs)

    def replace_rule(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_rule with MagicMock.
        """
        return self.mock_replace_rule(self, *args, **kwargs)

    def replace_runtime_status(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.replace_runtime_status with MagicMock.
        """
        return self.mock_replace_runtime_status(self, *args, **kwargs)

    def update_patch_application(self, *args, **kwargs):
        """
        This method mocks the original api ApplicationsApi.update_patch_application with MagicMock.
        """
        return self.mock_update_patch_application(self, *args, **kwargs)


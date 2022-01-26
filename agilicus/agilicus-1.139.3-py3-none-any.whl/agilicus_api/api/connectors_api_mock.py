from unittest.mock import MagicMock

class ConnectorsApiMock:

    def __init__(self):
        self.mock_create_agent_connector = MagicMock()
        self.mock_create_agent_csr = MagicMock()
        self.mock_create_agent_stats = MagicMock()
        self.mock_create_csr = MagicMock()
        self.mock_create_ipsec_connector = MagicMock()
        self.mock_delete_agent_connector = MagicMock()
        self.mock_delete_connector = MagicMock()
        self.mock_delete_ipsec_connector = MagicMock()
        self.mock_get_agent_connector = MagicMock()
        self.mock_get_agent_csr = MagicMock()
        self.mock_get_agent_info = MagicMock()
        self.mock_get_agent_stats = MagicMock()
        self.mock_get_connector = MagicMock()
        self.mock_get_ipsec_connector = MagicMock()
        self.mock_get_ipsec_connector_info = MagicMock()
        self.mock_list_agent_connector = MagicMock()
        self.mock_list_agent_csr = MagicMock()
        self.mock_list_connector = MagicMock()
        self.mock_list_ipsec_connector = MagicMock()
        self.mock_replace_agent_connector = MagicMock()
        self.mock_replace_agent_connector_local_auth_info = MagicMock()
        self.mock_replace_agent_csr = MagicMock()
        self.mock_replace_ipsec_connector = MagicMock()

    def create_agent_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.create_agent_connector with MagicMock.
        """
        return self.mock_create_agent_connector(self, *args, **kwargs)

    def create_agent_csr(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.create_agent_csr with MagicMock.
        """
        return self.mock_create_agent_csr(self, *args, **kwargs)

    def create_agent_stats(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.create_agent_stats with MagicMock.
        """
        return self.mock_create_agent_stats(self, *args, **kwargs)

    def create_csr(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.create_csr with MagicMock.
        """
        return self.mock_create_csr(self, *args, **kwargs)

    def create_ipsec_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.create_ipsec_connector with MagicMock.
        """
        return self.mock_create_ipsec_connector(self, *args, **kwargs)

    def delete_agent_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.delete_agent_connector with MagicMock.
        """
        return self.mock_delete_agent_connector(self, *args, **kwargs)

    def delete_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.delete_connector with MagicMock.
        """
        return self.mock_delete_connector(self, *args, **kwargs)

    def delete_ipsec_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.delete_ipsec_connector with MagicMock.
        """
        return self.mock_delete_ipsec_connector(self, *args, **kwargs)

    def get_agent_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_agent_connector with MagicMock.
        """
        return self.mock_get_agent_connector(self, *args, **kwargs)

    def get_agent_csr(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_agent_csr with MagicMock.
        """
        return self.mock_get_agent_csr(self, *args, **kwargs)

    def get_agent_info(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_agent_info with MagicMock.
        """
        return self.mock_get_agent_info(self, *args, **kwargs)

    def get_agent_stats(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_agent_stats with MagicMock.
        """
        return self.mock_get_agent_stats(self, *args, **kwargs)

    def get_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_connector with MagicMock.
        """
        return self.mock_get_connector(self, *args, **kwargs)

    def get_ipsec_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_ipsec_connector with MagicMock.
        """
        return self.mock_get_ipsec_connector(self, *args, **kwargs)

    def get_ipsec_connector_info(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.get_ipsec_connector_info with MagicMock.
        """
        return self.mock_get_ipsec_connector_info(self, *args, **kwargs)

    def list_agent_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.list_agent_connector with MagicMock.
        """
        return self.mock_list_agent_connector(self, *args, **kwargs)

    def list_agent_csr(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.list_agent_csr with MagicMock.
        """
        return self.mock_list_agent_csr(self, *args, **kwargs)

    def list_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.list_connector with MagicMock.
        """
        return self.mock_list_connector(self, *args, **kwargs)

    def list_ipsec_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.list_ipsec_connector with MagicMock.
        """
        return self.mock_list_ipsec_connector(self, *args, **kwargs)

    def replace_agent_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.replace_agent_connector with MagicMock.
        """
        return self.mock_replace_agent_connector(self, *args, **kwargs)

    def replace_agent_connector_local_auth_info(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.replace_agent_connector_local_auth_info with MagicMock.
        """
        return self.mock_replace_agent_connector_local_auth_info(self, *args, **kwargs)

    def replace_agent_csr(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.replace_agent_csr with MagicMock.
        """
        return self.mock_replace_agent_csr(self, *args, **kwargs)

    def replace_ipsec_connector(self, *args, **kwargs):
        """
        This method mocks the original api ConnectorsApi.replace_ipsec_connector with MagicMock.
        """
        return self.mock_replace_ipsec_connector(self, *args, **kwargs)


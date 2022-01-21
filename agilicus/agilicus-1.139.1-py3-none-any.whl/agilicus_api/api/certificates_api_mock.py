from unittest.mock import MagicMock

class CertificatesApiMock:

    def __init__(self):
        self.mock_create_cert = MagicMock()
        self.mock_delete_agent_csr = MagicMock()
        self.mock_delete_cert = MagicMock()
        self.mock_delete_csr = MagicMock()
        self.mock_get_cert = MagicMock()
        self.mock_get_csr = MagicMock()
        self.mock_list_certs = MagicMock()
        self.mock_list_csr = MagicMock()
        self.mock_replace_csr = MagicMock()

    def create_cert(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.create_cert with MagicMock.
        """
        return self.mock_create_cert(self, *args, **kwargs)

    def delete_agent_csr(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.delete_agent_csr with MagicMock.
        """
        return self.mock_delete_agent_csr(self, *args, **kwargs)

    def delete_cert(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.delete_cert with MagicMock.
        """
        return self.mock_delete_cert(self, *args, **kwargs)

    def delete_csr(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.delete_csr with MagicMock.
        """
        return self.mock_delete_csr(self, *args, **kwargs)

    def get_cert(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.get_cert with MagicMock.
        """
        return self.mock_get_cert(self, *args, **kwargs)

    def get_csr(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.get_csr with MagicMock.
        """
        return self.mock_get_csr(self, *args, **kwargs)

    def list_certs(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.list_certs with MagicMock.
        """
        return self.mock_list_certs(self, *args, **kwargs)

    def list_csr(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.list_csr with MagicMock.
        """
        return self.mock_list_csr(self, *args, **kwargs)

    def replace_csr(self, *args, **kwargs):
        """
        This method mocks the original api CertificatesApi.replace_csr with MagicMock.
        """
        return self.mock_replace_csr(self, *args, **kwargs)


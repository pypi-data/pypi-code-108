from unittest.mock import MagicMock

class CataloguesApiMock:

    def __init__(self):
        self.mock_create_catalogue = MagicMock()
        self.mock_create_catalogue_entry = MagicMock()
        self.mock_delete_catalogue = MagicMock()
        self.mock_delete_catalogue_entry = MagicMock()
        self.mock_get_catalogue = MagicMock()
        self.mock_get_catalogue_entry = MagicMock()
        self.mock_list_all_catalogue_entries = MagicMock()
        self.mock_list_catalogue_entries = MagicMock()
        self.mock_list_catalogues = MagicMock()
        self.mock_replace_catalogue = MagicMock()
        self.mock_replace_catalogue_entry = MagicMock()

    def create_catalogue(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.create_catalogue with MagicMock.
        """
        return self.mock_create_catalogue(self, *args, **kwargs)

    def create_catalogue_entry(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.create_catalogue_entry with MagicMock.
        """
        return self.mock_create_catalogue_entry(self, *args, **kwargs)

    def delete_catalogue(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.delete_catalogue with MagicMock.
        """
        return self.mock_delete_catalogue(self, *args, **kwargs)

    def delete_catalogue_entry(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.delete_catalogue_entry with MagicMock.
        """
        return self.mock_delete_catalogue_entry(self, *args, **kwargs)

    def get_catalogue(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.get_catalogue with MagicMock.
        """
        return self.mock_get_catalogue(self, *args, **kwargs)

    def get_catalogue_entry(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.get_catalogue_entry with MagicMock.
        """
        return self.mock_get_catalogue_entry(self, *args, **kwargs)

    def list_all_catalogue_entries(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.list_all_catalogue_entries with MagicMock.
        """
        return self.mock_list_all_catalogue_entries(self, *args, **kwargs)

    def list_catalogue_entries(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.list_catalogue_entries with MagicMock.
        """
        return self.mock_list_catalogue_entries(self, *args, **kwargs)

    def list_catalogues(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.list_catalogues with MagicMock.
        """
        return self.mock_list_catalogues(self, *args, **kwargs)

    def replace_catalogue(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.replace_catalogue with MagicMock.
        """
        return self.mock_replace_catalogue(self, *args, **kwargs)

    def replace_catalogue_entry(self, *args, **kwargs):
        """
        This method mocks the original api CataloguesApi.replace_catalogue_entry with MagicMock.
        """
        return self.mock_replace_catalogue_entry(self, *args, **kwargs)


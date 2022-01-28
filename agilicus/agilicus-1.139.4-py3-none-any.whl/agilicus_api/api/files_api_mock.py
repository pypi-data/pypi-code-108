from unittest.mock import MagicMock

class FilesApiMock:

    def __init__(self):
        self.mock_add_file = MagicMock()
        self.mock_delete_file = MagicMock()
        self.mock_get_download = MagicMock()
        self.mock_get_file = MagicMock()
        self.mock_list_files = MagicMock()
        self.mock_replace_file = MagicMock()

    def add_file(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.add_file with MagicMock.
        """
        return self.mock_add_file(self, *args, **kwargs)

    def delete_file(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.delete_file with MagicMock.
        """
        return self.mock_delete_file(self, *args, **kwargs)

    def get_download(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.get_download with MagicMock.
        """
        return self.mock_get_download(self, *args, **kwargs)

    def get_file(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.get_file with MagicMock.
        """
        return self.mock_get_file(self, *args, **kwargs)

    def list_files(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.list_files with MagicMock.
        """
        return self.mock_list_files(self, *args, **kwargs)

    def replace_file(self, *args, **kwargs):
        """
        This method mocks the original api FilesApi.replace_file with MagicMock.
        """
        return self.mock_replace_file(self, *args, **kwargs)


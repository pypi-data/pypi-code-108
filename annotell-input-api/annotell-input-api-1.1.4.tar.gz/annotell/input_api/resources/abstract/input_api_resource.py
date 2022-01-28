from annotell.input_api.cloud_storage import FileResourceClient
from annotell.input_api.http_client import HttpClient


class InputAPIResource:

    def __init__(self, client: HttpClient, file_client: FileResourceClient):
        super().__init__()
        self._client = client
        self._file_client = file_client

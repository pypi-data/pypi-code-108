
from typing import List
from azure.storage.blob import BlobServiceClient
from . import storage_backend

class AzureBlobStorageBackend(storage_backend.StorageBackend[str, bytes]):
    def __init__(self, connection_string: str, container_name: str):
        self._container_client = (BlobServiceClient
                .from_connection_string(connection_string)
                .get_container_client(container_name))

    def _blob_client(self, name: str):
        return self._container_client.get_blob_client(name)

    def store(self, key: str, value: bytes) -> None:
        """
        retrieve
        ========

        parameters:
            key (str)
            value (bytes)

        Stores the data in a blob, overwriting it if it exists.
        """

        if (client := self._blob_client(key)).exists():
            client.delete_blob()

        client.upload_blob(value)

    def retrieve(self, key: str) -> bytes:
        """
        retrieve
        ========

        parameters:
            key (str)
        returns:
            bytes

        Fetches the contents of a blob
        """
        if (client := self._blob_client(key)).exists():
            return client.download_blob().readall()
        else:
            raise KeyError(f"{key} does not exist")

    def exists(self, key: str) -> bool:
        """
        exists
        ===========

        parameters:
            path (str): The path to a file on the server

        returns:
            bool: Whether file exists or not

        For a given key check if the blob exists
        """
        return self._blob_client(key).exists()

    def keys(self) -> List[str]:
        """
        keys
        ====

        returns:
            List[str]

        Returns the names of all of the blobs currently stored.
        """
        return [blob.name for blob in self._container_client.list_blobs()]

    def __del__(self):
        self._container_client.close()

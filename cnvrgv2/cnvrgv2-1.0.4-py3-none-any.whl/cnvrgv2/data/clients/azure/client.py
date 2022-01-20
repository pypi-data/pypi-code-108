from azure.storage.blob import BlobServiceClient

from cnvrgv2.config import error_messages
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.utils.converters import convert_bytes
from cnvrgv2.utils.retry import retry
from cnvrgv2.utils.storage_utils import create_dir_if_not_exists
from cnvrgv2.data.clients.base_storage_client import BaseStorageClient


class AzureStorage(BaseStorageClient):
    def __init__(self, storage_meta):
        super().__init__(storage_meta)

        props = self._decrypt_dict(storage_meta, keys=[
            "container",
            "storage_access_key",
            "storage_account_name",
        ])
        account_name = props["storage_account_name"]
        account_key = props["storage_access_key"]
        container = props["container"]

        self.access_key = (
            "DefaultEndpointsProtocol=https;"
            "AccountName={};"
            "AccountKey={};"
            "EndpointSuffix=core.windows.net"
        ).format(
            account_name,
            account_key
        )
        self.container_name = container
        self.service = self._get_service()

    @retry(log_error=True)
    def upload_single_file(self, local_path, object_path, progress_bar=None):

        try:
            client = self.service.get_blob_client(container=self.container_name, blob=object_path)
            file_total = [0]
            progress_callback = self.progress_callback(progress_bar, file_total=file_total)
            with open(local_path, "rb") as local_file:
                client.upload_blob(local_file, max_concurrency=1, overwrite=True, raw_response_hook=progress_callback)
        except Exception as e:
            print(e)

    @retry(log_error=True)
    def download_single_file(self, local_path, object_path, progress_bar=None):
        try:
            client = self.service.get_blob_client(container=self.container_name, blob=object_path)
            create_dir_if_not_exists(local_path)
            file_total = [0]
            progress_callback = self.progress_callback(progress_bar, file_total=file_total)
            with open(local_path, "wb") as local_file:
                local_file.write(client.download_blob(max_concurrency=1, raw_response_hook=progress_callback).readall())
        except Exception as e:
            print(e)

    def progress_callback(self, progress_bar, file_total):
        if file_total is None:
            raise CnvrgArgumentsError(error_messages.FILE_TOTAL)

        def progress_incrementer(response):
            if progress_bar and progress_bar.max > 0:
                with progress_bar.mutex:
                    bytes_received = response.context['download_stream_current'] or response.context[
                        'upload_stream_current']
                    if bytes_received is None:
                        return

                    converted_bytes, unit = convert_bytes(bytes_received, unit=progress_bar.unit)
                    # Only the bytes sent/received
                    progress_bar.throttled_next(converted_bytes - file_total[0])
                    file_total[0] = converted_bytes

        return progress_incrementer

    def _get_service(self):
        return BlobServiceClient.from_connection_string(self.access_key)

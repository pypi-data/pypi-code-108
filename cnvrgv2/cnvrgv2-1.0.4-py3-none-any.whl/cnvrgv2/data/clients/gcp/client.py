import mimetypes
import os
import google.auth.transport.requests as tr_requests
from google.oauth2 import service_account
from google.resumable_media.requests import ChunkedDownload, ResumableUpload
from cnvrgv2.utils.retry import retry
from cnvrgv2.config import CONFIG_FOLDER_NAME
from cnvrgv2.utils.storage_utils import download_file, create_dir_if_not_exists
from cnvrgv2.data.clients.base_storage_client import BaseStorageClient


class GCPStorage(BaseStorageClient):
    def __init__(self, storage_meta):
        super().__init__(storage_meta)
        self.chunk_size = 262144 * 5  # needs to be a multiply of 256 kb. 262144 bytes = 256 kb

        self.key_file = os.path.join(os.path.expanduser("~"), CONFIG_FOLDER_NAME, ".gcp_cred.json")

        props = self._decrypt_dict(storage_meta, keys=["credentials"])

        download_file(props["credentials"], self.key_file)

        self.transport = self._get_transport()
        self.download_url_template = 'https://storage.googleapis.com/cnvrg-storage/{object_path}'
        self.upload_url = 'https://www.googleapis.com/upload/storage/v1/b/cnvrg-storage/o/?uploadType=resumable'
        self.credential_scope = 'https://www.googleapis.com/auth/devstorage.read_write'

    @retry(log_error=True)
    def upload_single_file(self, local_path, object_path, progress_bar):
        try:
            progress_incrementer = self.progress_callback(progress_bar)
            metadata = {'name': object_path}
            content_type = mimetypes.guess_type(local_path, strict=True)[0] or "plain/text"
            media_url = self.upload_url.format(object_path=object_path)

            with open(local_path, "rb") as file_stream:
                # Creates a ResumableUpload object that allows to transmit data in chunks.
                # Needs to be followed by an initiate command, that makes the first request to gcp, and gets
                # essential information for the uploading process to work
                upload = ResumableUpload(media_url, self.chunk_size)
                upload.initiate(self.transport, file_stream, metadata, content_type)
                while not upload.finished:
                    last_bytes_uploaded = upload.bytes_uploaded
                    upload.transmit_next_chunk(self.transport)
                    last_bytes_uploaded = upload.bytes_uploaded - last_bytes_uploaded
                    progress_incrementer(last_bytes_uploaded)

        except Exception as e:
            print(e)

    @retry(log_error=True)
    def download_single_file(self, local_path, object_path, progress_bar=None):
        try:
            progress_incrementer = self.progress_callback(progress_bar)
            media_url = self.download_url_template.format(object_path=object_path)
            create_dir_if_not_exists(local_path)
            with open(local_path, "wb") as file_stream:
                download = ChunkedDownload(media_url, self.chunk_size, file_stream)
                while not download.finished:
                    response = download.consume_next_chunk(self.transport)
                    progress_incrementer(len(response.content))

        except Exception as e:
            print(e)

    def _get_transport(self):
        credentials = service_account.Credentials.from_service_account_file(self.key_file)
        scoped_credentials = credentials.with_scopes([self.credential_scope])
        return tr_requests.AuthorizedSession(scoped_credentials)

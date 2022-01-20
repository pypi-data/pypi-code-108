import requests

from abc import ABC, abstractmethod
from cnvrgv2.utils.storage_utils import decrypt
from cnvrgv2.config import Config
from cnvrgv2.utils.converters import convert_bytes


class BaseStorageClient(ABC):
    def __init__(self, storage_meta):
        sts_url = storage_meta.get("sts_url")

        sts_content = requests.get(sts_url, verify=False).text
        sts_array = sts_content.split("\n")
        self.iv = sts_array[1]
        self.key = sts_array[0]
        self.check_certificate = Config().check_certificate or False

    def progress_callback(self, progress_bar):
        def progress_incrementer(bytes_received):
            if progress_bar and progress_bar.max > 0:
                converted_bytes, unit = convert_bytes(bytes_received, unit=progress_bar.unit)
                with progress_bar.mutex:
                    progress_bar.throttled_next(converted_bytes)

        return progress_incrementer

    def _decrypt_dict(self, props, keys=None):
        """
        Decrypt storage meta from the server.
        @param props: the storage meta dictionary
        @param keys: keys we want to decrypt
        @return: decrypted dictionary
        """

        # Only decrypts keys in props, otherwise leaves value unchanged
        return {k: decrypt(self.key, self.iv, v) if k in keys else v for k, v in props.items()}

    @abstractmethod
    def upload_single_file(self, local_path, object_path):
        """
        Uploads a single file using the relevant client
        @param local_path: The local path from which to upload
        @param object_path: The remote file path in the object storage service
        @return: None
        """
        pass

    @abstractmethod
    def download_single_file(self, local_path, object_path):
        """
        Downloads a single file using the relevant client
        @param local_path: The local path to which to download
        @param object_path: The remote file path in the object storage service
        @return:
        """
        pass

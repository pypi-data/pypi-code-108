import boto3
import botocore

from boto3.s3.transfer import TransferConfig

from cnvrgv2.utils.retry import retry
from cnvrgv2.utils.storage_utils import create_dir_if_not_exists
from cnvrgv2.data.clients.base_storage_client import BaseStorageClient


config = TransferConfig(max_concurrency=10, use_threads=True)


class MinioStorage(BaseStorageClient):
    def __init__(self, storage_meta):
        super().__init__(storage_meta)

        props = self._decrypt_dict(storage_meta, keys=["sts_a", "sts_s", "sts_st", "bucket", "region", "endpoint"])

        self.s3props = {
            "endpoint_url": props.get("endpoint"),
            "aws_access_key_id": props.get("sts_a"),
            "aws_secret_access_key": props.get("sts_s"),
            "region_name": props.get("region")
        }
        self.bucket = props.get("bucket")
        self.region = props.get("region")
        self.client = self._get_client()

    @retry(log_error=True)
    def upload_single_file(self, local_path, object_path, progress_bar=None):
        try:
            self.client.upload_file(
                local_path,
                self.bucket,
                object_path,
                Config=config,
                Callback=self.progress_callback(progress_bar)
            )
        except Exception as e:
            print(e)

    @retry(log_error=True)
    def download_single_file(self, local_path, object_path, progress_bar=None):
        try:
            create_dir_if_not_exists(local_path)
            self.client.download_file(
                self.bucket,
                object_path,
                local_path,
                Config=config,
                Callback=self.progress_callback(progress_bar)
            )
        except Exception as e:
            raise e

    def _get_client(self):
        botocore_config = botocore.config.Config(max_pool_connections=50)
        return boto3.client('s3', config=botocore_config, verify=self.check_certificate, **self.s3props)

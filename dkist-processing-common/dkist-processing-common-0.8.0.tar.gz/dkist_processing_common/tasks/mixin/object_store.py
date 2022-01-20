"""
Mixin for a WorkflowDataTaskBase subclass which implements Object Store data access functionality
"""
import json
from os import environ
from pathlib import Path
from typing import Union

from object_clerk import ObjectClerk

from dkist_processing_common._util.config import get_mesh_config


class ObjectStoreMixin:
    @property
    def _object_store_retry_configuration(self) -> dict:
        retry_configuration = environ.get(
            "RETRY_CONFIG",
            '{"retry_delay":1,"retry_backoff":2,"retry_jitter":[1,10],"retry_max_delay":300}',
        )
        retry_configuration = json.loads(retry_configuration)
        retry_configuration["retry_jitter"] = tuple(retry_configuration["retry_jitter"])
        return retry_configuration

    @property
    def _object_store_connection_configuration(self) -> dict:
        mesh_config = get_mesh_config()
        conn_config = {
            "host": mesh_config["object-store-api"]["mesh_address"],
            "port": mesh_config["object-store-api"]["mesh_port"],
            "access_key": environ.get("OBJECT_STORE_ACCESS_KEY", None),
            "secret_key": environ.get("OBJECT_STORE_SECRET_KEY", None),
            "use_ssl": False,
        }
        return conn_config

    @property
    def object_store_client(self) -> ObjectClerk:
        """
        The object store client is additionally configured by the following environment variables:
          MULTIPART_THRESHOLD - Threshold in bytes at which uploads are broken into multiple parts
            for upload. Impacts the checksum stored in the eTag
          S3_CLIENT_CONFIG - https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
          S3_UPLOAD_CONFIG - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig
        """
        retry_config = self._object_store_retry_configuration
        conn_config = self._object_store_connection_configuration
        return ObjectClerk(**conn_config, **retry_config)

    def object_store_upload_movie(
        self,
        movie: Union[Path, bytes],
        bucket: str,
        object_key: str,
        content_type: str = "video/mp4",
    ):
        self.object_store_client.upload_object(
            object_data=movie,
            bucket=bucket,
            object_key=object_key,
            verify_checksum=True,
            content_type=content_type,
            metadata={"groupname": "DATASET", "groupid": self.dataset_id, "objecttype": "MOVIE"},
        )

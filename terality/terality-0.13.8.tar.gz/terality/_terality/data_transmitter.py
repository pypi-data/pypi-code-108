import hashlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
from typing import Any, Iterator, Optional, Tuple, Union
import boto3
from botocore import UNSIGNED
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

from common_client_scheduler import AwsCredentials
from common_client_scheduler.config import (
    SessionInfo,
    SessionInfoLocal,
    SessionInfoType,
    TransferConfig,
)
from terality.exceptions import TeralityClientError

OBJECT_CHUNK_SIZE_BYTES = 200 * 1024 * 1024  # objects to copy are copied chunk by chunk


class S3:
    # Authentication
    # ~~~~~~~~~~~~~~
    #
    # We use the S3 client in two configurations:
    # * local to S3 copies, or S3 to local copies (where S3 is a Terality owned bucket)
    # * S3 to S3 copies (between a user and a Terality owned bucket)
    #
    # While the user may have her own AWS credentials in her environment, we can't use them to write to
    # Terality buckets. Indeed, regardless of bucket policies, the user won't be able to perform a PutObject
    # (or CreateMultipartUpload) on a Terality bucket without a policy giving him "s3:PutObject" on said
    # bucket. Same goes for reads.
    #
    # Instead, whenever the client needs to perform a write or read operation on a Terality bucket,
    # it retrieves short-lived, temporary AWS credentials from the Terality API suitable for the operation.
    #
    # This is simpler than having the server generate pre-signed URLs, and provides the same level of
    # security.
    #
    # However, Terality-issued credentials can't be used to read or write S3 files to user buckets.
    #
    # We force the signature_version to s3v4 (signature version 4) to avoid edge cases where the user
    # would have set another default signature version.
    _client: Any = None
    _client_with_credentials: Any = None
    _client_anonymous: Any = None
    _credentials: Optional[AwsCredentials] = None

    @classmethod
    def client(cls):
        """An S3 client using user credentials (using the default boto3 loading mecanism).

        Operations with this client will fail if the user has no AWS credentials available in their
        environment.
        """
        if cls._client is None:
            cls._client = boto3.session.Session().client(
                "s3", config=Config(max_pool_connections=200, signature_version="s3v4")
            )
        return cls._client

    @classmethod
    def client_from_credentials(cls, credentials: AwsCredentials):
        """An authenticated S3 client, with temporary credentials provided by Terality."""
        if cls._credentials != credentials:
            cls._client_with_credentials = boto3.session.Session().client(
                "s3",
                config=Config(max_pool_connections=200, signature_version="s3v4"),
                aws_access_key_id=credentials.access_key_id,
                aws_secret_access_key=credentials.secret_access_key,
                aws_session_token=credentials.session_token,
            )
            cls._credentials = credentials
        return cls._client_with_credentials

    @classmethod
    def client_anonymous(cls):
        """An anonymous S3 client, since the user IAM role may have permission blocked to
        s3 buckets not in his account"""
        if cls._client_anonymous is None:
            cls._client_anonymous = boto3.session.Session().client(
                "s3", config=Config(signature_version=UNSIGNED)
            )
        return cls._client_anonymous


_ACL = {"ACL": "bucket-owner-full-control"}


class DataTransmitter(metaclass=ABCMeta):
    """
    Interface to perform uploads and downloads to/from the Terality servers.

    A transfer ID (referenced here in several places) is an identifier of the
    location of uploaded files, or of files to be downloaded. The server
    and the client can use transfer IDs to locate files.
    """

    # The production implementation of this is DataTransmitterS3, where files
    # are exchanged with Terality through S3.
    # During testing, it can be swapped for an implementation using a local
    # filesystem instead. The abstraction level is not perfect here, and S3
    # details leak into this interface. This is not a real issue for now
    # (as we only use two known subclasses, one in production and one during
    # local tests), this can be cleaned up over time.
    # Also, note that cloud to Terality transfers don't use this interface - we copy
    # from cloud to cloud instead.

    @abstractmethod
    def set_current_session(self, session: Optional[SessionInfoType]) -> None:
        """Set the session to be used to perform data transfers."""

    @abstractmethod
    def get_upload_aws_region(self) -> str:
        """Return the AWS region containg the S3 bucket used to perform uploads.

        Subclasses that don't use S3 may chose not to support this and can raise a NotImplementedError.
        """

    @abstractmethod
    def get_download_source_bucket_and_prefix(
        self, aws_region: Optional[str], transfer_id: str
    ) -> Tuple[str, str]:
        """Return an AWS bucket and prefix where files to be exported are stored

        Subclasses that don't use S3 may chose not to support this and can raise a NotImplementedError.
        """

    @abstractmethod
    def upload_bytes(self, aws_credentials: AwsCredentials, data: BytesIO) -> str:
        """Upload a buffer to Terality servers. Return the transfer ID."""

    @abstractmethod
    def upload_local_file(
        self,
        aws_credentials: AwsCredentials,
        local_file: str,
        file_suffix: str,
        cache_disabled: bool,
    ) -> None:
        """Upload a local file to Terality servers."""

    @abstractmethod
    def download_to_bytes(self, aws_credentials: AwsCredentials, transfer_id) -> BytesIO:
        """Download a file from the Terality servers."""

    @abstractmethod
    def download_to_local_files(
        self,
        aws_credentials: AwsCredentials,
        transfer_id: str,
        path: str,
        is_folder: bool,
        with_leading_zeros: bool,
    ):
        """Download files from the Terality servers."""


class DataTransmitterS3(DataTransmitter):
    """
    Interface to perform uploads and downloads to/from S3.
    """

    def __init__(self):
        self._session: Optional[SessionInfo] = None

    def get_download_source_bucket_and_prefix(self, aws_region: Optional[str], transfer_id: str):
        download_config = self._get_download_config()
        source_bucket = download_config.bucket_region(aws_region)
        source_prefix = f"{download_config.key_prefix}{transfer_id}/"
        return source_bucket, source_prefix

    def get_upload_aws_region(self) -> str:
        return self._get_upload_config().default_aws_region

    def set_current_session(self, session: Optional[Union[SessionInfo, SessionInfoLocal]]) -> None:
        if session is None:
            self._session = None
            return

        if not isinstance(session, SessionInfo):
            raise ValueError(f"Type of session must be SessionInfo, got {type(session)}.")
        self._session = session

    def _get_upload_config(self) -> TransferConfig:
        if self._session is None:
            raise ValueError("A session must be open to be able to perform data transfers.")
        return self._session.upload_config

    def _get_download_config(self) -> TransferConfig:
        if self._session is None:
            raise ValueError("A session must be open to be able to perform data transfers.")
        return self._session.download_config

    def upload_bytes(self, aws_credentials: AwsCredentials, data: BytesIO) -> str:
        data.seek(0)
        sha512 = hashlib.sha512()
        for chunk in iter(lambda: data.read(4_194_304), b""):
            sha512.update(chunk)
        transfer_id = sha512.hexdigest()
        data.seek(0)

        key = f"{self._get_upload_config().key_prefix}{transfer_id}/0.data"
        client = S3.client_from_credentials(aws_credentials)

        if not object_exists(
            client=client, bucket=self._get_upload_config().bucket_region(), key=key
        ):
            client.upload_fileobj(
                Fileobj=data,
                Bucket=self._get_upload_config().bucket_region(),
                Key=key,
                ExtraArgs=_ACL,
            )

        return transfer_id

    def upload_local_file(
        self,
        aws_credentials: AwsCredentials,
        local_file: str,
        file_suffix: str,
        cache_disabled: bool,
    ) -> None:
        key = f"{self._get_upload_config().key_prefix}{file_suffix}"
        client = S3.client_from_credentials(aws_credentials)

        if not cache_disabled and object_exists(
            client, self._get_upload_config().bucket_region(), key
        ):
            return

        client.upload_file(
            Bucket=self._get_upload_config().bucket_region(),
            Key=key,
            Filename=local_file,
            ExtraArgs=_ACL,
        )

    def download_to_bytes(self, aws_credentials: AwsCredentials, transfer_id: str) -> BytesIO:
        buf = BytesIO()
        key = f"{self._get_download_config().key_prefix}{transfer_id}/0.parquet"
        S3.client_from_credentials(aws_credentials).download_fileobj(
            Bucket=self._get_download_config().bucket_region(), Key=key, Fileobj=buf
        )
        return buf

    def download_to_local_files(
        self,
        aws_credentials: AwsCredentials,
        transfer_id: str,
        path: str,
        is_folder: bool,
        with_leading_zeros: bool,
    ) -> None:
        bucket = self._get_download_config().bucket_region()
        key_prefix = f"{self._get_download_config().key_prefix}{transfer_id}/"
        client = S3.client_from_credentials(aws_credentials)
        keys = [o[0] for o in list_all_objects_under_prefix(client, bucket, key_prefix)]
        if is_folder:
            dirname = os.path.dirname(path)
            filename = os.path.basename(path)
            Path(dirname).mkdir(parents=True, exist_ok=True)
            for num, key in enumerate(keys):
                file_num = f"{num:0{len(str(len(keys)))}d}" if with_leading_zeros else str(num + 1)
                client.download_file(
                    Bucket=bucket,
                    Key=key,
                    Filename=f"{dirname}/{filename.replace('*', file_num)}",
                )
        else:
            client.download_file(Bucket=bucket, Key=keys[0], Filename=path)


def list_all_objects_under_prefix(
    client: BaseClient, s3_bucket: str, s3_key_prefix: str
) -> Iterator[Tuple[str, int]]:
    """List all S3 keys in a bucket starting with a given prefix.

    Yield:
        tuples of (S3 object key, object size in bytes)
    """
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key_prefix)
    try:
        for page in page_iterator:
            objects = page["Contents"]
            for obj in objects:
                yield (obj["Key"], obj["Size"])
    except KeyError as e:
        raise TeralityClientError(
            "No object found under the specified S3 prefix, please check that the path you have entered is valid"
        ) from e


@dataclass
class ExportedS3File:
    """A S3 object stored in a Terality export bucket."""

    bucket: str
    key: str
    size_bytes: int


def object_exists(client: BaseClient, bucket: str, key: str) -> bool:
    try:
        client.head_object(
            Bucket=bucket,
            Key=key,
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404" or e.response["Error"]["Code"] == "403":
            return False
        raise e

"""Azure integration. Don't import this module at the top level of another module.

This module depends on the Azure Python SDK which is an extra (optional) depedency. You need to handle
import errors when you try to import this module.
"""
from datetime import datetime, timedelta
import logging
import os

from azure.storage.blob._shared.models import UserDelegationKey
from terality._terality.data_transmitter import (
    ExportedS3File,
    OBJECT_CHUNK_SIZE_BYTES,
    S3,
    list_all_objects_under_prefix,
)
from typing import Dict, Iterator, List, Optional, Tuple, Union, cast

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas
from azure.storage.filedatalake import FileSystemClient

from common_client_scheduler.requests import (
    AzureBlobSource,
    ImportFromAzureBlobStorageSource,
    AzureBlobStoragePartExportRequest,
    AzureBlobStoragePartsExport,
)
from common_client_scheduler import (
    AwsCredentials,
    StorageService,
    ObjectStorageKey,
    ImportFromCloudRequest,
    ExportToCloudRequest,
)

from .. import global_client

logger = logging.getLogger("azure")
logger.setLevel(logging.ERROR)


def upload_azure_storage_files(storage_account_name: str, container: str, folder: str) -> str:
    credential, storage_account_key = _get_azure_storage_credentials()

    blob_account_url, datalake_account_url = _storage_account_urls_from_name(storage_account_name)
    blob_service_client = BlobServiceClient(account_url=blob_account_url, credential=credential)
    start_time, expiry_time = _get_signature_time_range()

    signature = _get_signature_key(
        blob_service_client, storage_account_key, start_time, expiry_time
    )
    filesystem_client = FileSystemClient(datalake_account_url, container, credential=credential)
    objects_to_copy = list(
        list_objects_to_copy(
            container=container,
            folder=folder,
            storage_account_name=storage_account_name,
            expiry_time=expiry_time,
            start_time=start_time,
            signature=signature,
            blob_service_client=blob_service_client,
            filesystem_client=filesystem_client,
        )
    )
    return _send_transfer_request(objects_to_copy)


def _get_signature_time_range() -> Tuple[datetime, datetime]:
    start_time = datetime.utcnow()
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    return start_time, expiry_time


def _storage_account_urls_from_name(storage_account_name: str) -> Tuple[str, str]:
    datalake_account_url = f"https://{storage_account_name}.dfs.core.windows.net"
    blob_account_url = f"https://{storage_account_name}.blob.core.windows.net"
    return blob_account_url, datalake_account_url


def _get_azure_storage_credentials() -> Tuple[Union[str, DefaultAzureCredential], Optional[str]]:
    storage_account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    if storage_account_key is not None:
        credential = storage_account_key
    else:
        credential = DefaultAzureCredential()
    return credential, storage_account_key


def list_objects_to_copy(
    *,
    storage_account_name: str,
    container: str,
    folder: str,
    signature: Union[Dict[str, UserDelegationKey], Dict[str, str]],
    expiry_time: datetime,
    start_time: datetime,
    blob_service_client: BlobServiceClient,
    filesystem_client: FileSystemClient,
) -> Iterator[AzureBlobSource]:
    for path in _list_blobs(filesystem_client, folder):
        shared_access_signature = generate_blob_sas(
            account_name=storage_account_name,
            container_name=container,
            blob_name=path,
            permission="r",
            expiry=expiry_time,
            start_time=start_time,
            **signature,
        )
        blob_client = blob_service_client.get_blob_client(container, path)
        blob_size = cast(int, blob_client.get_blob_properties().size)
        for (range_start_byte, range_end_byte) in _make_chunks(blob_size):
            yield AzureBlobSource(
                object_key=ObjectStorageKey(bucket=container, key=path),
                shared_access_signature=shared_access_signature,
                storage_account_name=storage_account_name,
                range_start_byte=range_start_byte,
                range_end_byte=range_end_byte,
            )


def _get_signature_key(
    blob_service_client: BlobServiceClient,
    storage_account_key: Optional[str],
    start_time: datetime,
    expiry_time: datetime,
) -> Union[Dict[str, UserDelegationKey], Dict[str, str]]:
    if storage_account_key is None:
        user_delegation_key = blob_service_client.get_user_delegation_key(
            key_start_time=start_time, key_expiry_time=expiry_time
        )
        signature = {"user_delegation_key": user_delegation_key}
    else:
        signature = {"account_key": storage_account_key}
    return signature


def _send_transfer_request(objects_to_copy: List[AzureBlobSource]) -> str:
    request = ImportFromCloudRequest(
        service=StorageService.AZURE_BLOB_STORAGE,
        source=ImportFromAzureBlobStorageSource(objects=objects_to_copy),
    )
    response = global_client().poll_for_answer("imports/cloud", request)
    return response.transfer_id


def _list_blobs(client: FileSystemClient, folder: str) -> Iterator[str]:
    for path in client.get_paths(folder):
        if path.is_directory:
            yield from _list_blobs(client, path)
        else:
            yield path.name


def _make_chunks(
    object_size: int, chunk_size: int = OBJECT_CHUNK_SIZE_BYTES
) -> Iterator[Tuple[int, int]]:
    """Split the given size in consecutive ranges of chunk_size bytes (offsets are inclusive)."""
    range_start = 0
    while range_start < object_size:
        range_end = min(range_start + chunk_size, object_size) - 1
        yield (range_start, range_end)
        range_start = range_end + 1


def copy_to_azure_datalake(
    *,
    aws_credentials: AwsCredentials,
    transfer_id: str,
    aws_region: Optional[str],
    storage_account_name: str,
    container: str,
    path_template: str,
) -> None:
    """Copy the files identified by `transfer_id` from a Terality export bucket to an Azure Datalake Gen2 filesystem..

    Args:
        aws_credentials: AWS credentials to use to read files in the Terality export bucket
        transfer_id: transfer ID used to identify the files to copy from the Terality export bucket
        aws_region: AWS region hosting the Terality export bucket
        storage_account_name: destination Azure storage account
        container: destination Azure container
        path_template: destination path, with the pattern "some/path/*.extension". The '*' will be replaced by integers
            (starting from 0) in the destination.
    """
    source_bucket, source_prefix = (
        global_client()
        .data_transfer()
        .get_download_source_bucket_and_prefix(aws_region=aws_region, transfer_id=transfer_id)
    )

    auth_s3_client = S3.client_from_credentials(aws_credentials)
    files = [
        (
            path_template.replace("*", str(i)),
            ExportedS3File(bucket=source_bucket, key=s3_key, size_bytes=object_size),
        )
        for i, (s3_key, object_size) in enumerate(
            list_all_objects_under_prefix(auth_s3_client, source_bucket, source_prefix)
        )
    ]
    _copy_exported_files_to_azure_destination(files, storage_account_name, container)


def _copy_exported_files_to_azure_destination(
    files: List[Tuple[str, ExportedS3File]], storage_account_name: str, container: str
) -> None:
    credential, storage_account_key = _get_azure_storage_credentials()
    blob_account_url, _ = _storage_account_urls_from_name(storage_account_name)
    blob_service_client = BlobServiceClient(account_url=blob_account_url, credential=credential)
    start_time, expiry_time = _get_signature_time_range()
    signature = _get_signature_key(
        blob_service_client, storage_account_key, start_time, expiry_time
    )

    to_copy = list(
        _generate_blob_parts(
            files=files,
            storage_account_name=storage_account_name,
            container=container,
            expiry_time=expiry_time,
            start_time=start_time,
            signature=signature,
        )
    )
    request = ExportToCloudRequest(
        service=StorageService.AZURE_BLOB_STORAGE,
        export_request=AzureBlobStoragePartsExport(parts=to_copy),
    )
    global_client().poll_for_answer("exports/cloud", request)


def _generate_blob_parts(
    *,
    files: List[Tuple[str, ExportedS3File]],
    storage_account_name: str,
    container: str,
    expiry_time: datetime,
    start_time: datetime,
    signature: Dict,
) -> Iterator[AzureBlobStoragePartExportRequest]:
    for (destination_path, s3_file) in files:
        shared_access_signature = generate_blob_sas(
            account_name=storage_account_name,
            container_name=container,
            blob_name=destination_path,
            permission="w",
            expiry=expiry_time,
            start_time=start_time,
            **signature,
        )
        for (range_start_byte, range_end_byte) in _make_chunks(s3_file.size_bytes):
            yield AzureBlobStoragePartExportRequest(
                source_object_key=ObjectStorageKey(s3_file.bucket, s3_file.key),
                range_start_byte=range_start_byte,
                range_end_byte=range_end_byte,
                destination_object_key=ObjectStorageKey(bucket=container, key=destination_path),
                storage_account_name=storage_account_name,
                shared_access_signature=shared_access_signature,
            )

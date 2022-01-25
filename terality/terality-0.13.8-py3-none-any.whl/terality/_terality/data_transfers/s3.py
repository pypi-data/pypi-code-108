from itertools import groupby
from operator import attrgetter, itemgetter
from typing import Dict, Iterator, List, Tuple, Optional

from botocore.client import BaseClient
from botocore.exceptions import ClientError, NoCredentialsError
from common_client_scheduler import (
    AwsCredentials,
    StorageService,
    AwsPresignedUrlSource,
    ObjectStorageKey,
    ImportFromS3Source,
    ImportFromCloudRequest,
    AwsS3ObjectPartExportRequest,
    AwsS3PartsExport,
    ExportToCloudRequest,
    ExportToS3Response,
)

from .. import logger, global_client
from terality._terality.data_transmitter import (
    ExportedS3File,
    OBJECT_CHUNK_SIZE_BYTES,
    list_all_objects_under_prefix,
    S3,
)


def _generate_presigned_urls(
    client: BaseClient,
    s3_bucket: str,
    s3_key: str,
    object_size: int,
    part_size_bytes: int = 200 * 1024 * 1024,
) -> Iterator[AwsPresignedUrlSource]:
    """Generate pre-signed URLs allowing to read part of a S3 object.

    This function provides a few guarantees, that the server is relying on:
    * for each object, the URLs cover contiguous byte ranges of this object
    * the URLs are sorted by part number
    """
    range_start_byte = 0
    while range_start_byte < object_size:
        # byte range are inclusive
        range_end_byte = min(range_start_byte + part_size_bytes, object_size) - 1
        expiration = 3600
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": s3_bucket, "Key": s3_key},
            ExpiresIn=expiration,
        )
        yield AwsPresignedUrlSource(
            url=url,
            range_start_byte=range_start_byte,
            range_end_byte=range_end_byte,
            object_key=ObjectStorageKey(bucket=s3_bucket, key=s3_key),
        )
        range_start_byte = range_end_byte + 1


def _try_head_object_on_key(client, s3_bucket: str, s3_key: str):
    client.head_object(
        Bucket=s3_bucket,
        Key=s3_key,
    )


def _generate_upload_presigned_urls(client, s3_bucket: str, s3_key_prefix: str) -> list:
    presigned_urls = []
    for file_index, (s3_key, object_size) in enumerate(
        list_all_objects_under_prefix(client, s3_bucket, s3_key_prefix)
    ):
        # Verify that the client can call HeadObject on the first element before generating URLs
        # to avoid 403 errors when the server tries to access them using the generated URLs.
        # Listing the objects is not a guarantee that the client has also the permission to read them.
        # We suppose that a successful HeadObject on the first element is enough to say that client have the same access right to all of the other files.
        if file_index == 0:
            _try_head_object_on_key(client, s3_bucket, s3_key)
        presigned_urls += list(_generate_presigned_urls(client, s3_bucket, s3_key, object_size))
    return presigned_urls


def upload_s3_files(s3_bucket: str, s3_key_prefix: str) -> str:
    """
    Copy files from a source (user-owned) S3 bucket to a Terality-owned S3 bucket.

    Generate pre-signed URL for each chunk of each object to transfer, then send all these URLs to the
    Terality API. Terality will perform the copy server-side. The user AWS credentials are only used to
    generate these pre-signed URLs and are never sent to Terality.

    Assumes that the user has read permissions on all objects to be copied. Uses the boto3 standard
    credentials discovery mecanism.

    Args:
        s3_bucket: source S3 bucket
        s3_key_prefix: source S3 objects

    Return:
        a transfer ID. This ID can then be used as input to "read_csv/read_parquet" requests.
    """
    try:
        presigned_urls = _generate_upload_presigned_urls(S3.client(), s3_bucket, s3_key_prefix)
    except (ClientError, NoCredentialsError) as e:
        # retry as an anonymous client if the user IAM account blocks S3 access to buckets in other accounts, or the client has no credentials
        try:
            presigned_urls = _generate_upload_presigned_urls(
                S3.client_anonymous(), s3_bucket, s3_key_prefix
            )
        except Exception:
            # if it fails too re-raise the original exception
            raise e from None
    request = ImportFromCloudRequest(
        service=StorageService.AWS_S3,
        source=ImportFromS3Source(presigned_urls=presigned_urls),
        cache_disabled=global_client().cache_disabled(),
    )
    response = global_client().poll_for_answer("imports/cloud", request)
    return response.transfer_id


def copy_to_user_s3_bucket(
    aws_credentials: AwsCredentials,
    transfer_id: str,
    aws_region: Optional[str],
    destination_s3_path: str,
) -> None:
    """Copy the files identified by `transfer_id` from a Terality export bucket to a user S3 bucket.

    Args:
        aws_credentials: AWS credentials to use to read files in the Terality export bucket
        transfer_id: transfer ID used to identify the files to copy from the Terality export bucket
        aws_region: AWS region hosting the Terality export bucket
        destination_s3_path: a string of the form 's3://bucket/some/key/*.extension'. The '*' will be replaced
            by integers (starting from 0) in the destination.
    """
    if not destination_s3_path.startswith("s3://"):
        raise ValueError(
            f"destination_s3_path must start with 's3://', got '{destination_s3_path}'"
        )

    source_bucket, source_prefix = (
        global_client()
        .data_transfer()
        .get_download_source_bucket_and_prefix(aws_region=aws_region, transfer_id=transfer_id)
    )

    destination_s3_bucket, destination_s3_prefix_template = destination_s3_path[
        len("s3://") :
    ].split("/", maxsplit=1)

    auth_s3_client = S3.client_from_credentials(aws_credentials)
    files = [
        (
            destination_s3_prefix_template.replace("*", str(i)),
            ExportedS3File(bucket=source_bucket, key=s3_key, size_bytes=object_size),
        )
        for i, (s3_key, object_size) in enumerate(
            list_all_objects_under_prefix(auth_s3_client, source_bucket, source_prefix)
        )
    ]

    s3_client = S3.client()
    _copy_exported_files_to_s3_destination(s3_client, files, destination_s3_bucket)


def _copy_exported_files_to_s3_destination(  # pylint: disable=too-many-locals
    s3_client, files_to_copy: List[Tuple[str, ExportedS3File]], destination_s3_bucket: str
) -> None:
    """Copy S3 objects to a destination bucket.

    Args:
        s3_client: a botocore S3 client with enough permissions to write objects to the destination bucket
        files_to_copy: a list of (destination S3 key, source file to copy)
        destination_s3_bucket: destination S3 bucket
    """
    # TODO: this method is too long, clean that up
    presigned_urls = []
    uploads_in_progress: Dict[str, Tuple[str, str]] = {}  # dict of upload_id => (bucket, key)
    try:
        # Start multipart uploads and prepare presigned URLs
        for destination_s3_key, file_to_copy in files_to_copy:
            res = s3_client.create_multipart_upload(
                Bucket=destination_s3_bucket,
                Key=destination_s3_key,
            )
            upload_id = res["UploadId"]
            uploads_in_progress[upload_id] = (destination_s3_bucket, destination_s3_key)
            urls = _generate_upload_part_presigned_urls(
                s3_client,
                upload_id=upload_id,
                destination_s3_bucket=destination_s3_bucket,
                destination_s3_key=destination_s3_key,
                object_size_bytes=file_to_copy.size_bytes,
            )
            presigned_urls += [
                AwsS3ObjectPartExportRequest(
                    presigned_url=url[0],
                    destination_object_key=ObjectStorageKey(
                        bucket=destination_s3_bucket, key=destination_s3_key
                    ),
                    source_object_key=ObjectStorageKey(
                        bucket=file_to_copy.bucket, key=file_to_copy.key
                    ),
                    multipart_upload_id=upload_id,
                    part_number=part_number,
                    range_start_byte=url[1],
                    range_end_byte=url[2],
                )
                for part_number, url in enumerate(
                    urls, 1
                )  # part numbers start at 1 in the AWS S3 API
            ]

        # Send request to the API
        request = ExportToCloudRequest(
            service=StorageService.AWS_S3,
            export_request=AwsS3PartsExport(parts=presigned_urls),
        )
        export_res: ExportToS3Response = global_client().poll_for_answer("exports/cloud", request)

        # Complete the uploads
        parts = export_res.uploaded_parts
        keyfunc = attrgetter("multipart_upload_id")
        parts_by_upload_id = groupby(sorted(parts, key=keyfunc), key=keyfunc)
        for upload_id, parts in parts_by_upload_id:  # type: ignore
            parts = list(parts)
            etags = [
                {
                    "PartNumber": part.part_number,
                    "ETag": part.etag,
                }
                for part in parts
            ]
            bucket = parts[0].destination_object_key.bucket
            key = parts[0].destination_object_key.key
            etags = sorted(etags, key=itemgetter("PartNumber"))
            s3_client.complete_multipart_upload(
                UploadId=upload_id,
                Bucket=bucket,
                Key=key,
                MultipartUpload={"Parts": etags},
            )
            del uploads_in_progress[upload_id]
    finally:
        # Cancel uploads that were not completed to avoid the user being charged for data
        for upload_id, (bucket, key) in uploads_in_progress.items():
            try:
                logger.info(
                    f"Aborting multipart upload on s3://{bucket}/{key} (upload ID {upload_id})."
                )
                s3_client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
            except Exception:
                logger.exception(
                    f"Error when aborting multipart upload on s3://{bucket}/{key} (upload ID {upload_id})."
                )


def _generate_upload_part_presigned_urls(
    s3_client: BaseClient,
    *,
    upload_id: str,
    destination_s3_bucket: str,
    destination_s3_key: str,
    object_size_bytes: int,
    part_size_bytes: int = OBJECT_CHUNK_SIZE_BYTES,
) -> List[Tuple[str, int, int]]:
    """
    Generate presigned URLs for the AWS UploadPart S3 API.

    To write an object of size `object_size_bytes`, we'll call UploadPart on each object part. Thus,
    we need to generate one presigned URL per part.

    Args:
        s3_client: a S3 boto3 client
        upload_id: multipart upload ID, as returned by CreateMultipartUpload
        destination_s3_bucket: S3 bucket containing the destination S3 object
        destination_s3_key: S3 key of the object to write
        object_size_bytes: total size, in bytes, of the object to write
        part_size_bytes: maximum size of a part to upload.

    Return:
        a list of tuples (presigned URL, start byte, end byte)
    """
    expiration = 3600
    range_start_byte = 0
    part_number = 1
    out = []
    while range_start_byte < object_size_bytes:
        range_end_byte = min(range_start_byte + part_size_bytes, object_size_bytes) - 1
        url = s3_client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": destination_s3_bucket,
                "Key": destination_s3_key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=expiration,
        )
        out.append((url, range_start_byte, range_end_byte))

        part_number += 1
        range_start_byte = range_end_byte + 1
    return out

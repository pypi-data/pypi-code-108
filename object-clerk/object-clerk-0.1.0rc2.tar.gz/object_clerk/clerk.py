"""
API (ObjectClerk) definition
"""
import logging
from hashlib import md5
from io import BufferedReader
from io import BytesIO
from pathlib import Path
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from boto3 import client as Boto3Client
from botocore.exceptions import ClientError
from retry import retry
from retry.api import retry_call

from object_clerk.config import CHECKSUM_RETRY_CONFIG
from object_clerk.config import CLIENT_CONFIG
from object_clerk.config import CONNECTION_RETRY_EXCEPTIONS
from object_clerk.config import MULTIPART_THRESHOLD
from object_clerk.config import UPLOAD_CONFIG
from object_clerk.exceptions import ObjectSaveException
from object_clerk.exceptions import ObjectVerificationException
from object_clerk.utils import client_exception_handler
from object_clerk.utils import mutate_client_exceptions

logger = logging.getLogger(__name__)

# Configure boto to not retry; handled by the retry api


__all__ = ["ObjectClerk"]


class ObjectClerk:
    """
    A wrapper for the following boto3 s3 client operations:
    boto3.client.func : object_clerk.func
    - get_object : get_object
    - head_object : get_object_info
    - upload_fileobj : upload_object
    - copy_object : copy_object
    - delete_object : delete_object

    Environment configuration:
    MULTIPART_THRESHOLD : The threshold for multi part uploads.  Uploads and downloads have to use
      the same threshold for the checksum algorithm to verify integrity.  Default is 8 MB.
    """

    def __init__(
        self,
        host: str,
        port: int,
        access_key: str,
        secret_key: str,
        retry_delay: int,
        retry_backoff: int,
        retry_jitter: Union[int, Tuple[int, int]],
        retry_max_delay: int,
        retry_tries: int = -1,
        use_ssl: bool = False,
        list_objects_page_size=1000,
    ):
        """
        Initialize the Object clerk with the location of the s3 gateway
        and configuration for retrying connection issues
        :param host: Host name or ip for an s3 Gateway
        :param port: Post the s3 gateway listens on
        :param access_key: Access Key for the gateway
        :param secret_key: Secret Key for the gateway
        :param retry_delay: initial delay between attempts for connection errors.
        :param retry_backoff: multiplier applied to delay between attempts to connect.
        :param retry_jitter: extra seconds added to delay between attempts to connect.
                   fixed if a number, random if a range tuple (min, max)
        :param retry_max_delay: the maximum value of delay between connection attempts.
        :param retry_tries: Number of time to retry connecting ot hte gateway. -1 for indefinite
          retries
        :param use_ssl: True for https and False for http
        :param list_objects_page_size: size of page to retrieve while listing objects in a bucket.
          smaller sizes result in less memory usage but more calls to the object store.
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.retry_jitter = retry_jitter
        self.retry_max_delay = retry_max_delay
        self.retry_tries = retry_tries
        self.use_ssl = use_ssl
        self.list_objects_page_size = list_objects_page_size
        self.retry_config = {
            "tries": self.retry_tries,
            "delay": self.retry_delay,
            "max_delay": self.retry_max_delay,
            "backoff": self.retry_backoff,
            "jitter": self.retry_jitter,
            "exceptions": CONNECTION_RETRY_EXCEPTIONS,
        }
        protocol = "https" if self.use_ssl else "http"
        self.endpoint_url = f"{protocol}://{self.host}:{self.port}"
        self.client = Boto3Client(
            service_name="s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            config=CLIENT_CONFIG,
        )
        logger.info(str(self))

    def __repr__(self):
        return (
            f"ObjectClerk(host={self.host}, port={self.port}, access_key={self.access_key}, "
            f"secret_key=<SECRET KEY>, retry_delay={self.retry_delay}, retry_backoff={self.retry_backoff}, "
            f"retry_jitter={self.retry_jitter}, retry_max_delay={self.retry_max_delay}, "
            f"retry_tries={self.retry_tries}, use_ssl={self.use_ssl})"
        )

    def __str__(self):
        return f"ObjectClerk connected to {self.endpoint_url} retrying connection errors with {self.retry_config}"

    @staticmethod
    def _get_object_checksum(object_stream: bytes) -> str:
        """
        Get the s3 checksum of a bytestream
            - md5 hexdigest for objects below the multipart threshold
            - md5 hexdigest of md5s of each part for objects equal
                to or greater than the multipart threshold with
                a "-" followed by the number of parts
        :param object_stream: bytes to create a checksum for
        :return: str s3 checksum
        """
        # Load object in a bytes reader to support chunking
        reader = BytesIO(object_stream)
        checksums = []

        # Accumulate checksums while there are more chunks
        while True:
            data = reader.read(MULTIPART_THRESHOLD)  # retrieve chunk
            if not data:
                break  # No more chunks
            checksums.append(md5(data))

        if len(checksums) == 0:  # Empty object stream
            return md5(object_stream).hexdigest()

        # at precisely the multipart threshold the object is not
        # broken up into multiple parts but the checksum algorithm
        # is calculated as if it was
        if len(object_stream) < MULTIPART_THRESHOLD:
            return checksums[0].hexdigest()  # Non-multipart upload

        # Build byte string of the concatenated md5s of each chunk
        chunk_md5s = b"".join([c.digest() for c in checksums])

        # concatenate md5 of the md5 string with - and the number of chunks
        return f"{md5(chunk_md5s).hexdigest()}-{len(checksums)}"

    @staticmethod
    def _verify_checksum(object_checksum: str, etag: str) -> None:
        """
        Verify the checksum matches the etag response from an s3 gateway
        :param object_checksum: checksum of the bytes object
        :param etag: checksum from the s3 api
        :return: None
        :raises: ObjectVerificationException if the the checksums don't match
        """
        # Strip leading and trailing quotes on the etag if they exist
        etag = etag.replace('"', "")
        if object_checksum == etag:
            return
        raise ObjectVerificationException(
            f"Object checksum verification failed: check_sum={object_checksum}, etag={etag}"
        )

    @mutate_client_exceptions
    def _get_object(self, bucket: str, object_key: str) -> bytes:
        """
        Executes the boto3.client.get_object function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param bucket: Bucket to retrieve the object from
        :param object_key: Key of the object in the bucket
        :return: bytes of the object retrieved
        """
        logger.debug(f"Attempting object retrieval: bucket={bucket}, object_key={object_key}")
        return self.client.get_object(Bucket=bucket, Key=object_key)

    @retry(ObjectVerificationException, **CHECKSUM_RETRY_CONFIG)
    def get_object(self, bucket: str, object_key: str, verify_checksum: bool = True) -> bytes:
        """
        Retrieves a bytes object from an S3 endpoint retrying connection errors
        according to object clerk instance attributes
        errors according to object_clerk definition
        :param bucket: Bucket to retrieve the object from
        :param object_key: Key of the object in the bucket
        :param verify_checksum: boolean to determine whether or not to verify the
          checksum of the retrieved bytes against the etag
        :return: bytes of the object retrieved
        :raises: ObjectNotFoundException, ObjectClerkException, ObjectVerificationException,
          ObjectClerkServerAuthException
        """
        response = retry_call(
            self._get_object,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )
        object_stream = response.get("Body").read()
        etag = response.get("ETag")
        if verify_checksum:
            checksum = self._get_object_checksum(object_stream)
            self._verify_checksum(checksum, etag)
        return object_stream

    @mutate_client_exceptions
    def _get_object_info(self, bucket: str, object_key: str) -> dict:
        """
        Executes the boto3.client.head_object function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param bucket: Bucket to retrieve headers for the object from
        :param object_key: Key of the object in the bucket
        :return: dict of the object s3 headers
        """
        logger.debug(f"Attempting object info retrieval: bucket={bucket}, object_key={object_key}")
        return self.client.head_object(Bucket=bucket, Key=object_key)

    def get_object_info(self, bucket: str, object_key: str) -> dict:
        """
        Retrieves a headers for an object from an S3 endpoint retrying connection errors
        according to object clerk instance attributes
        :param bucket: Bucket to retrieve headers for the object from
        :param object_key: Key of the object in the bucket
        :return: dict of the object s3 headers
        :raises: ObjectNotFoundException, ObjectClerkException, ObjectClerkServerAuthException
        """
        response = retry_call(
            self._get_object_info,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )
        return response["ResponseMetadata"].get("HTTPHeaders")

    @mutate_client_exceptions
    def _delete_object(self, bucket: str, object_key: str) -> None:
        """
        Executes the boto3.client.delete_object function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param bucket: Bucket to delete the object from
        :param object_key: Key of the object in the bucket to delete
        :return: None
        """
        logger.debug(f"Attempting object delete: bucket={bucket}, object_key={object_key}")
        self.client.delete_object(Bucket=bucket, Key=object_key)

    def delete_object(self, bucket: str, object_key: str) -> None:
        """
        Deletes an object from an S3 endpoint retrying connection errors
        according to object clerk instance attributes
        :param bucket: Bucket to delete the object from
        :param object_key: Key of the object in the bucket to delete
        :return: None
        :raises: ObjectNotFoundException, ObjectClerkException, ObjectClerkServerAuthException
        """
        retry_call(
            self._delete_object,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )

    @staticmethod
    def _data_to_bytes(data: Union[str, Path, BufferedReader, BytesIO, bytes]) -> bytes:
        """
        Transform multiple types into a bytes object
        :param data: variable to convert
        :return: file converted to bytes
        """
        if isinstance(data, bytes):
            return data
        if isinstance(data, (BufferedReader, BytesIO)):
            data.seek(0)  # support retry
            return data.read()
        if isinstance(data, str):
            data = Path(data)
        if not isinstance(data, Path):
            raise TypeError("file must be of one of type str, Path, BufferedReader, BytesIO, bytes")
        try:
            data = data.open(mode="rb")
            bytes_obj = data.read()
            data.close()
        except OSError as e:
            raise ObjectSaveException(f"File cannot be opened: detail={e}")
        return bytes_obj

    @mutate_client_exceptions
    def _upload_object(
        self,
        bytes_obj: bytes,
        bucket: str,
        object_key: str,
        content_type: str,
        metadata: dict,
        storage_class: str = None,
    ) -> None:
        """
        Executes the boto3.client.upload_fileobj function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param bucket: Bucket to upload the object to
        :param object_key: Key of the object in the bucket to upload to
        :param bytes_obj: bytes to upload
        :param content_type: Content type of the file to be uploaded.  Will be added to the
          ExtraArgs as Content-Type
        :param metadata: metadata for the file to be uploaded.  Will be added to the ExtraArgs as
          Metadata
        :param storage_class: Storage class of the object. e.g DEEP_ARCHIVE for AWS Glacier Deep
          Archive.  Will be added to the ExtraArgs as StorageClass
        :return: None
        """
        logger.debug(f"Attempting object upload: bucket={bucket}, object_key={object_key}")
        extra_args = {"ContentType": content_type, "Metadata": metadata}
        if storage_class:
            extra_args["StorageClass"] = storage_class
        self.client.upload_fileobj(
            BytesIO(bytes_obj),
            Bucket=bucket,
            Key=object_key,
            Config=UPLOAD_CONFIG,
            ExtraArgs=extra_args,
        )

    @retry(ObjectVerificationException, **CHECKSUM_RETRY_CONFIG)
    def upload_object(
        self,
        object_data: Union[str, Path, BufferedReader, BytesIO, bytes],
        bucket: str,
        object_key: str,
        verify_checksum: bool = True,
        content_type: str = "application/octet-stream",
        metadata: dict = None,
        storage_class: str = None,
    ) -> None:
        """
        Uploads a data to the specified bucket and object key retrying connection errors according
          to instance retry specification and checksum failures according to internal config
          if requested (default)
        :param object_data: Data to upload
        :param bucket: Bucket to upload to
        :param object_key: Object Key in the bucket for the object after upload
        :param verify_checksum: Boolean indicator of whether to verify the checksum of the
          uploaded file matches
        what is in the S3 bucket
        :param content_type: Content type of the file to be uploaded.  Will be added to the
          ExtraArgs as Content-Type
        :param metadata: metadata for the file to be uploaded.  Will be added to the
          ExtraArgs as Metadata
        :param storage_class: Storage class of the object. e.g DEEP_ARCHIVE for AWS Glacier Deep
          Archive.  Will be added to the ExtraArgs as StorageClass
        :return: None
        :raises: ObjectVerificationException, ObjectSaveException, ObjectClerkException,
          ObjectClerkServerAuthException
        """
        metadata = metadata or {}
        bytes_obj = self._data_to_bytes(object_data)
        # get checksum before boto operations
        checksum = self._get_object_checksum(bytes_obj)
        if checksum == md5(b"").hexdigest():
            raise ObjectSaveException("Attempt to upload an empty file not allowed.")
        retry_call(
            self._upload_object,
            fkwargs={
                "bytes_obj": bytes_obj,
                "bucket": bucket,
                "object_key": object_key,
                "content_type": content_type,
                "metadata": metadata,
                "storage_class": storage_class,
            },
            **self.retry_config,
        )
        if verify_checksum:
            etag = self.get_object_info(bucket, object_key).get("etag")
            try:
                self._verify_checksum(checksum, etag)
            except ObjectVerificationException as e:
                logger.warning(f"Saved object does not match check sum: detail={e}")
                self.delete_object(bucket, object_key)
                logger.debug(f"Saved object is removed: bucket={bucket}, object_key={object_key}")
                raise e

    @mutate_client_exceptions
    def _copy_object(
        self,
        source_bucket: str,
        source_object_key: str,
        destination_bucket: str,
        destination_object_key: str,
    ) -> None:
        """
        Execute boto3.client.copy_object function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param source_bucket: Bucket of the object being copied
        :param source_object_key: Object key of the object being copied
        :param destination_bucket: Bucket to copy to
        :param destination_object_key: Object key of the copied object
        :return: None
        """
        logger.debug(
            f"Attempting object retrieval: source_bucket={source_bucket}, "
            f"source_object_key={source_object_key}, destination_bucket={destination_bucket}, "
            f"destination_object_key={destination_object_key}"
        )
        copy_source = {"Bucket": source_bucket, "Key": source_object_key}
        self.client.copy(
            Bucket=destination_bucket,
            Key=destination_object_key,
            CopySource=copy_source,
            Config=UPLOAD_CONFIG,
        )

    @retry(exceptions=ObjectVerificationException, **CHECKSUM_RETRY_CONFIG)
    def copy_object(
        self,
        source_bucket: str,
        source_object_key: str,
        destination_bucket: str,
        destination_object_key: str,
        verify_checksum: bool = True,
    ) -> None:
        """
        Create a copy of an object in an existing s3 bucket in another location retrying
        connection errors according to instance retry specification and checksum failures
        according to internal config if requested (default)
        :param source_bucket: Bucket of the object being copied
        :param source_object_key: Object key of the object being copied
        :param destination_bucket: Bucket to copy to
        :param destination_object_key: Object key of the copied object
        :param verify_checksum: Boolean indicator of whether to verify the checksum of the
        copied file matches the original
        :return: None
        :raises: ObjectVerificationException, ObjectSaveException, ObjectClerkException, ObjectClerkServerAuthException
        """
        source_object_info = self.get_object_info(source_bucket, source_object_key)

        retry_call(
            self._copy_object,
            fkwargs={
                "source_bucket": source_bucket,
                "source_object_key": source_object_key,
                "destination_bucket": destination_bucket,
                "destination_object_key": destination_object_key,
            },
            **self.retry_config,
        )

        if verify_checksum:
            destination_object_info = self.get_object_info(
                destination_bucket, destination_object_key
            )
            if source_object_info["etag"] == destination_object_info["etag"]:
                return
            self.delete_object(destination_bucket, destination_object_key)
            logger.warning(
                f"Copied object does not match check sum: source_bucket={source_bucket}, "
                f"source_object_key={source_bucket}, source_checksum={source_object_info['etag']}, "
                f"destination_bucket={destination_bucket}, destination_object_key={destination_object_key}, "
                f"destination_check_sum={destination_object_info['etag']}"
            )
            self.delete_object(destination_bucket, destination_object_key)
            logger.debug(
                f"Copied object is removed: bucket={destination_bucket}, object_key={destination_object_key}"
            )
            raise ObjectVerificationException(
                f"Object checksum verification failed: "
                f"source_etag={source_object_info['etag']}, "
                f"destination_etag={destination_object_info['etag']}"
            )

    def move_object(
        self,
        source_bucket: str,
        source_object_key: str,
        destination_bucket: str,
        destination_object_key: str,
        verify_checksum: bool = True,
    ) -> None:
        """
        Copy an object in an existing s3 bucket in another location retrying
        connection errors according to instance retry specification and checksum failures
        according to internal config if requested (default) and delete the source object
        upon successful completion
        :param source_bucket: Bucket of the object being copied
        :param source_object_key: Object key of the object being copied and will be deleted
        :param destination_bucket: Bucket to copy to
        :param destination_object_key: Object key of the copied object
        :param verify_checksum: Boolean indicator of whether to verify the checksum of the
        copied file matches the original
        :return: None
        :raises: ObjectVerificationException, ObjectSaveException, ObjectClerkException, ObjectClerkServerAuthException
        """
        self.copy_object(
            source_bucket,
            source_object_key,
            destination_bucket,
            destination_object_key,
            verify_checksum,
        )
        self.delete_object(source_bucket, source_object_key)

    @mutate_client_exceptions
    def _list_objects(self, bucket: str, prefix: str = None) -> Generator[dict, None, None]:
        """
        Executes the boto3.client.list_objects_v2 function with ClientError exceptions
        transformed to more precise ObjectClerk exceptions
        :param bucket: Bucket to retrieve the object metadata from
        :param prefix: Limits the response to keys that begin with the specified prefix.
        :return: None
        """
        there_are_more_results_to_retrieve = True
        kwargs = {"Bucket": bucket, "MaxKeys": self.list_objects_page_size}
        response = {}
        if prefix:
            kwargs["Prefix"] = prefix
        while there_are_more_results_to_retrieve:
            try:
                response = self.client.list_objects_v2(**kwargs)
            except ClientError as e:
                client_exception_handler(e, function_name="list_objects_v2", args=(), kwargs=kwargs)
            there_are_more_results_to_retrieve = response.get("IsTruncated")
            for r in response.get("Contents", []):
                yield r
                kwargs["StartAfter"] = r["Key"]

    def list_objects(self, bucket: str, prefix: str = None) -> Generator[dict, None, None]:
        """
        Get the contents of a bucket retrying connection errors according to instance retry specification.
        :param bucket: Bucket to retrieve the object metadata from
        :param prefix: Limits the response to keys that begin with the specified prefix.
        :return: a generator of dictionaries, one dict for each object in `bucket`
        :raises: ObjectNotFoundException, ObjectClerkException, ObjectClerkServerAuthException
        """
        response = retry_call(
            self._list_objects,
            fkwargs={"bucket": bucket, "prefix": prefix},
            **self.retry_config,
        )
        return response

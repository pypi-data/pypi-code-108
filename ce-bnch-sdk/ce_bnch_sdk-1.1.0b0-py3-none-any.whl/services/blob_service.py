from io import BytesIO
import mimetypes
from pathlib import Path
import sys
import tempfile
from typing import cast, Iterable, List, Optional, Union

from benchling_api_client.api.blobs import (
    abort_multipart_blob,
    bulk_get_blobs,
    complete_multipart_blob,
    create_blob,
    create_blob_part,
    create_multipart_blob,
    get_blob,
    get_blob_url,
)
import httpx
from typing_extensions import Protocol

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.file_helpers import calculate_md5, encode_base64
from benchling_sdk.helpers.logging_helpers import sdk_logger
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import array_query_param
from benchling_sdk.models import (
    Blob,
    BlobComplete,
    BlobCreate,
    BlobCreateType,
    BlobMultipartCreate,
    BlobMultipartCreateType,
    BlobPart,
    BlobPartCreate,
    BlobUrl,
)
from benchling_sdk.services.base_service import BaseService

DEFAULT_HTTP_TIMEOUT: float = 60.0
# 10 MB in bytes
MINIMUM_CHUNK_SIZE_BYTES: int = int(10e6)
DEFAULT_CHUNK_SIZE_BYTES: int = MINIMUM_CHUNK_SIZE_BYTES


def _write_blob_file(file_contents: BytesIO, file_path: Optional[Path] = None) -> Path:
    """Write bytes to a file. Will create a temp file if file_path isn't specified.

    Returns the Path of the file written to, whether created or used.
    """
    if file_path:
        with open(file_path, "wb") as existing_file_handle:
            existing_file_handle.write(file_contents.getbuffer())
        return file_path
    handle, temp_file_path = tempfile.mkstemp()
    with open(handle, "wb") as temp_file_handle:
        temp_file_handle.write(file_contents.getbuffer())
    return Path(temp_file_path)


class _BytesReader(Protocol):
    def __call__(self, chunk_size_bytes: int) -> bytes:
        ...


class BlobService(BaseService):
    """
    Blobs.

    Blobs are opaque files that can be linked to other items in Benchling, like assay runs or results. For example,
    you can upload a blob, then upload an assay result that links to that blob by ID. The blob will then appear as
    part of the assay result in the Benchling web UI.

    See https://benchling.com/api/reference#/Blobs
    """

    @api_method
    def get_by_id(self, blob_id: str) -> Blob:
        """
        Get a Blob.

        See https://benchling.com/api/reference#/Blobs/getBlob
        """
        response = get_blob.sync_detailed(client=self.client, blob_id=blob_id)
        return model_from_detailed(response)

    @api_method
    def create(self, blob: BlobCreate, timeout_seconds: float = DEFAULT_HTTP_TIMEOUT) -> Blob:
        """
        Upload a single-part blob.

        Blobs larger than 10MB should be uploaded in multiple parts. The data64 parameter is the
        base64-encoded part contents, and the md5 parameter is the hex-encoded MD5 hash of the part
        contents. For example, given the string hello, data64 is aGVsbG8= and md5 is 5d41402abc4b2a76b9719d911017c592

        See https://benchling.com/api/reference#/Blobs/createBlob
        """
        timeout_client = self.client.with_timeout(timeout_seconds)
        response = create_blob.sync_detailed(client=timeout_client, json_body=blob)
        return model_from_detailed(response)

    @api_method
    def create_from_bytes(
        self,
        input_bytes: Union[BytesIO, bytes],
        name: str,
        mime_type: Optional[str] = None,
        blob_type: BlobCreateType = BlobCreateType.RAW_FILE,
        timeout_seconds: float = DEFAULT_HTTP_TIMEOUT,
        chunk_size_bytes: int = DEFAULT_CHUNK_SIZE_BYTES,
    ) -> Blob:
        """Create a Benchling Blob from bytes or a BytesIO stream.

        Will automatically attempt a multi-part upload if the stream appears larger
        than the API's maximum size for single Blobs.

        :param input_bytes: The bytes or stream to upload
        :param name: The name of the Blob in Benchling
        :param mime_type: The representative MIME type for the Blob
        :param blob_type: The type of Blob in Benchling (Visualization or Raw File)
        :param timeout_seconds: Extends the normal HTTP timeout settings since Blob uploads can be large
            Use this to extend even further if streams are very large
        :param chunk_size_bytes: The size in bytes for each chunk when using a multipart upload. If the
            bytes exceed chunk_size_bytes, multipart will automatically be attempted. Otherwise, single
            Blob upload will be used
        :return: The created Blob
        :rtype: Blob
        """
        self.validate_chunk_size(chunk_size_bytes)
        if not isinstance(input_bytes, BytesIO):
            input_bytes = BytesIO(input_bytes)
        bytes_size = sys.getsizeof(input_bytes)
        chunk_producer: _BytesReader = lambda chunk_size: input_bytes.read(chunk_size)
        if bytes_size > MINIMUM_CHUNK_SIZE_BYTES:
            sdk_logger.info(
                "Size of input (%s bytes) exceeds minimum chunk size of %s bytes, "
                "initiating multipart upload",
                bytes_size,
                MINIMUM_CHUNK_SIZE_BYTES,
            )
            return self._multipart_from_bytes(
                chunk_producer=chunk_producer,
                name=name,
                blob_type=self._multipart_type(blob_type),
                mime_type=mime_type,
                timeout_seconds=timeout_seconds,
                chunk_size_bytes=chunk_size_bytes,
            )
        else:
            contents = input_bytes.read()
            return self._create_blob(
                blob_input=contents,
                name=name,
                blob_type=blob_type,
                mime_type=mime_type,
                timeout_seconds=timeout_seconds,
            )

    @api_method
    def create_from_file(
        self,
        file_path: Path,
        name: Optional[str] = None,
        mime_type: Optional[str] = None,
        blob_type: BlobCreateType = BlobCreateType.RAW_FILE,
        auto_detect: bool = True,
        timeout_seconds: float = DEFAULT_HTTP_TIMEOUT,
        chunk_size_bytes: int = DEFAULT_CHUNK_SIZE_BYTES,
    ) -> Blob:
        """Create a Benchling Blob from a file.

        Will automatically attempt a multi-part upload if the file appears larger
        than the API's maximum size for single Blobs.

        :param file_path: The Path to the file to upload
        :param name: The name of the Blob in Benchling
        :param mime_type: The representative mime type for the Blob
        :param blob_type: The type of Blob in Benchling (Visualization or Raw File)
        :param auto_detect: Will attempt to guess the file's MIME type if mime_type was not specified
            and auto_detect is True
        :param timeout_seconds: Extends the normal HTTP timeout settings since Blob uploads can be large
            Use this to extend even further if streams are very large
        :param chunk_size_bytes: The size in bytes for each chunk when using a multipart upload. If the
            bytes exceed chunk_size_bytes, multipart will automatically be attempted. Otherwise, single
            Blob upload will be used
        :return: The created Blob
        :rtype: Blob
        """
        self.validate_chunk_size(chunk_size_bytes)
        if not (file_path.exists() and file_path.is_file()):
            raise FileNotFoundError(f"{file_path} does not exist or is not a valid file")
        if auto_detect:
            if not name:
                name = file_path.name
            if not mime_type:
                mime_type = mimetypes.guess_type(str(file_path))[0]
        else:
            assert name, "name must be provided if auto_detect is not set to True"
        with open(file_path, "rb") as file:
            file_size_bytes = file_path.stat().st_size
            if file_size_bytes > MINIMUM_CHUNK_SIZE_BYTES:
                sdk_logger.info(
                    "Size of %s (%s bytes) exceeds minimum chunk size of %s bytes, "
                    "initiating multipart upload",
                    str(file_path),
                    file_size_bytes,
                    MINIMUM_CHUNK_SIZE_BYTES,
                )
                chunk_producer: _BytesReader = lambda chunk_size: file.read(chunk_size)
                return self._multipart_from_bytes(
                    chunk_producer=chunk_producer,
                    name=name,
                    blob_type=self._multipart_type(blob_type),
                    mime_type=mime_type,
                    timeout_seconds=timeout_seconds,
                    chunk_size_bytes=chunk_size_bytes,
                )
            else:
                file_contents = file.read()
                return self.create_from_bytes(
                    input_bytes=file_contents,
                    name=name,
                    blob_type=blob_type,
                    mime_type=mime_type,
                    timeout_seconds=timeout_seconds,
                )

    @api_method
    def download_url(self, blob_id: str) -> BlobUrl:
        """
        Get a Blob's download URL.

        See https://benchling.com/api/reference#/Blobs/getBlobUrl
        """
        response = get_blob_url.sync_detailed(client=self.client, blob_id=blob_id)
        return model_from_detailed(response)

    @api_method
    def download_bytes(self, blob_id: str) -> BytesIO:
        """Download a Blob in its entirety from Benchling and write it to BytesIO."""
        blob_download_wrapper = self.download_url(blob_id)
        download_url = cast(str, blob_download_wrapper.download_url)
        response = httpx.get(download_url)
        return BytesIO(response.content)

    @api_method
    def download_file(self, blob_id: str, destination_path: Optional[Path] = None) -> Path:
        """
        Download a Blob from Benchling and writes it to a file.

        If specified, destination_path must be a reference to a file and not a directory.
        It must also not already exist on the file system. If destination_path is None,
        a temporary file will be created for writing.
        """
        if destination_path and destination_path.is_dir():
            raise IsADirectoryError(
                f"Cannot write blob to directory '{destination_path}', specify a file instead"
            )
        elif destination_path and destination_path.exists():
            raise FileExistsError(f"Cannot write blob to '{destination_path}', the file already exists")
        blob_bytes = self.download_bytes(blob_id)
        destination_path = _write_blob_file(blob_bytes, destination_path)
        if not destination_path.exists():
            raise FileNotFoundError(f"Unable to write blob {blob_id} to '{destination_path}'")
        return destination_path

    @api_method
    def bulk_get(self, blob_ids: Iterable[str]) -> List[Blob]:
        """
        Bulk get Blobs by UUID.

        See https://benchling.com/api/reference#/Blobs/bulkGetBlobs
        """
        blob_ids_string = array_query_param(blob_ids)
        response = bulk_get_blobs.sync_detailed(client=self.client, blob_ids=blob_ids_string)
        results_list = model_from_detailed(response)
        return results_list.blobs

    @api_method
    def create_multipart_upload(self, multipart_blob: BlobMultipartCreate) -> Blob:
        """
        Initiate multi-part Blob upload.

        See https://benchling.com/api/reference#/Blobs/createMultipartBlob
        """
        response = create_multipart_blob.sync_detailed(client=self.client, json_body=multipart_blob)
        return model_from_detailed(response)

    @api_method
    def create_part(
        self, blob_id: str, blob_part: BlobPartCreate, timeout_seconds: float = DEFAULT_HTTP_TIMEOUT
    ) -> BlobPart:
        """
        Upload a part of a multi-part Blob.

        Larger files and slower connections will likely need to set a higher timeout_seconds value in
        order to complete successful part uploads.

        See https://benchling.com/api/reference#/Blobs/createBlobPart
        """
        timeout_client = self.client.with_timeout(timeout_seconds)
        response = create_blob_part.sync_detailed(client=timeout_client, blob_id=blob_id, json_body=blob_part)
        return model_from_detailed(response)

    @api_method
    def complete_multipart_upload(self, blob_id: str, blob_parts: Iterable[BlobPart]) -> Blob:
        """
        Combine Blob parts into a single Blob.

        See https://benchling.com/api/reference#/Blobs/completeMultipartBlob
        """
        blob_complete = BlobComplete(parts=list(blob_parts))
        response = complete_multipart_blob.sync_detailed(
            client=self.client, blob_id=blob_id, json_body=blob_complete
        )
        return model_from_detailed(response)

    @api_method
    def abort_multipart_upload(self, blob_id: str) -> None:
        """
        Abort multi-part blob upload.

        See https://benchling.com/api/reference#/Blobs/abortMultipartBlob
        """
        response = abort_multipart_blob.sync_detailed(client=self.client, blob_id=blob_id)
        # Even though we won't return, will do the other processing such as status checking
        empty_object = model_from_detailed(response)  # noqa: F841

    def _create_blob(
        self,
        blob_input: bytes,
        name: str,
        blob_type: BlobCreateType,
        mime_type: Optional[str],
        timeout_seconds: float,
    ) -> Blob:
        data = encode_base64(blob_input)
        md5 = calculate_md5(blob_input)
        blob_create = BlobCreate(name=name, type=blob_type, data64=data, md5=md5)
        # Use BlobCreate's default mime type unless we specified one
        if mime_type is not None:
            blob_create.mime_type = mime_type
        return self.create(blob=blob_create, timeout_seconds=timeout_seconds)

    def _multipart_from_bytes(
        self,
        chunk_producer: _BytesReader,
        name: str,
        mime_type: Optional[str],
        blob_type: BlobMultipartCreateType,
        timeout_seconds: float,
        chunk_size_bytes: int,
    ) -> Blob:
        blob_parts = []
        part_number = 0
        multipart_args = {"name": name, "type": blob_type}
        # Do not override BlobMultipartCreate's mime_type unless explicitly set
        if mime_type:
            multipart_args["mime_type"] = mime_type
        multipart_blob = BlobMultipartCreate(**multipart_args)  # type: ignore
        start_blob = self.create_multipart_upload(multipart_blob=multipart_blob)
        try:
            while True:
                cursor = chunk_producer(chunk_size_bytes)
                if not cursor:
                    break
                part_number += 1
                sdk_logger.debug("Beginning upload of part %s for blob '%s'", part_number, name)
                created_part = self._upload_part(
                    parent_blob_id=start_blob.id,
                    part_number=part_number,
                    input_bytes=cursor,
                    timeout_seconds=timeout_seconds,
                )
                blob_parts.append(created_part)
            sdk_logger.info("Uploaded %s total parts of blob '%s', completing upload", part_number, name)
            completed_blob = self.complete_multipart_upload(blob_id=start_blob.id, blob_parts=blob_parts)
            return completed_blob
        except Exception as e:
            sdk_logger.error(
                "Error while uploading part %s for blob '%s', aborting upload", part_number, name
            )
            self.abort_multipart_upload(blob_id=start_blob.id)
            raise e

    def _upload_part(
        self, parent_blob_id: str, part_number: int, input_bytes: bytes, timeout_seconds: float
    ) -> BlobPart:
        data = encode_base64(input_bytes)
        md5 = calculate_md5(input_bytes)
        blob_part = BlobPartCreate(part_number=part_number, data64=data, md5=md5)
        created_part = self.create_part(
            blob_id=parent_blob_id, blob_part=blob_part, timeout_seconds=timeout_seconds
        )
        return created_part

    @staticmethod
    def validate_chunk_size(chunk_size_bytes: int):
        """Validate the specified bytes chunk size."""
        if chunk_size_bytes < MINIMUM_CHUNK_SIZE_BYTES:
            raise ValueError(
                f"chunk_size_bytes was {chunk_size_bytes}. "
                f"When specified, it must be at least the "
                f"minimum chunk size of {MINIMUM_CHUNK_SIZE_BYTES}"
            )

    @staticmethod
    def _multipart_type(blob_type: BlobCreateType):
        # TODO These models should probably be the same
        return BlobMultipartCreateType(blob_type.name)

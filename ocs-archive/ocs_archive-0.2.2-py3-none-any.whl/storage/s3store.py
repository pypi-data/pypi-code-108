from datetime import datetime, timedelta
import logging
from io import BytesIO
from contextlib import contextmanager

from dateutil.parser import parse
import boto3

from ocs_archive.input.file import DataFile
from ocs_archive.storage.filestore import FileStore, FileStoreConnectionError
from ocs_archive.settings import settings

logger = logging.getLogger('ocs_ingester')


def strip_quotes_from_etag(etag):
    """Amazon returns the md5 sum of the uploaded file in the 'ETag' header wrapped in quotes."""
    if etag.startswith('"') and etag.endswith('"'):
        return etag[1:-1]


class S3Store(FileStore):
    def __init__(self, bucket: str = settings.BUCKET):
        """Create an S3 file storage manager using the bucket specified."""
        super().__init__()
        self.bucket = bucket

    def get_s3_client(self):
        config = boto3.session.Config(signature_version=settings.S3_SIGNATURE_VERSION)
        return boto3.client('s3', endpoint_url=settings.S3_ENDPOINT_URL, config=config)

    def get_storage_class(self, observation_date):
        # if the observation was more than X days ago, this is someone
        # uploading older data, and it can skip straight to STANDARD_IA
        if observation_date < (datetime.utcnow() - timedelta(days=settings.S3_DAYS_TO_IA_STORAGE)):
            return 'STANDARD_IA'

        # everything else goes into the STANDARD storage class, and will
        # be switched to STANDARD_IA by S3 Lifecycle Rules
        return 'STANDARD'

    def store_file(self, data_file: DataFile):
        storage_class = self.get_storage_class(parse(data_file.get_header_data().get_observation_date()))
        # start_time = datetime.utcnow()
        s3 = boto3.resource('s3', endpoint_url=settings.S3_ENDPOINT_URL)
        key = data_file.get_filestore_path()
        content_disposition = 'attachment; filename={0}{1}'.format(data_file.open_file.basename, data_file.open_file.extension)
        content_type = data_file.get_filestore_content_type()
        try:
            response = s3.Object(self.bucket, key).put(
                Body=data_file.open_file.get_from_start(),
                ContentDisposition=content_disposition,
                ContentType=content_type,
                StorageClass=storage_class,
            )
        except Exception as exc:
            raise FileStoreConnectionError(exc)
        s3_md5 = strip_quotes_from_etag(response['ETag'])
        key = response['VersionId']
        logger.info('Ingester uploaded file to s3', extra={
            'tags': {
                'filename': '{}{}'.format(data_file.open_file.basename, data_file.open_file.extension),
                'key': key,
                'storage_class': storage_class,
            }
        })

        return {'key': key, 'md5': s3_md5, 'extension': data_file.open_file.extension}

    def delete_file(self, path: str, version_id: str):
        """
        Delete a file from s3.

        :param path: s3 path for file
        """
        client = self.get_s3_client()
        client.delete_object({
            'Bucket': self.bucket,
            'Key': path,
            'VersionId': version_id
        })

    def get_url(self, path: str, version_id: str, expiration: float):
        """
        Get a downloadable url for a file from s3.

        :param path: s3 path for file
        """
        client = self.get_s3_client()
        return client.generate_presigned_url(
            'get_object',
            ExpiresIn=expiration,
            Params={
                'Bucket': self.bucket,
                'Key': path,
                'VersionId': version_id
            }
        )

    @contextmanager
    def get_fileobj(self, path: str):
        """
        Get a file from s3.

        DataFile can contain an EmptyFile within it, but the headers must be correct
        To figure out the file storage path.

        :param data_file: DataFile with filled in headers pointing to storage path
        :return: File-like object
        """
        client = self.get_s3_client()
        fileobj = BytesIO()
        client.download_fileobj(Bucket=self.bucket,
                                Key=path,
                                Fileobj=fileobj)
        fileobj.seek(0)
        try:
            yield fileobj
        finally:
            fileobj.close()

    def get_file_size(self, path: str):
        """
        Get the size of a file in s3.

        :param path: s3 path for file
        :return: file size in bytes
        """
        client = self.get_s3_client()
        return client.head_object(Bucket=self.bucket, Key=path)['ContentLength']

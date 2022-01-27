from io import BytesIO
from contextlib import contextmanager

from ocs_archive.input.file import DataFile


class FileStoreConnectionError(Exception):
    """
    This exception should generally be caught and retried in the calling class,
    since it may just be a transient connection issue.
    """
    pass


class FileStoreSpecificationError(Exception):
    """This exception is for an invalid configured filestore, and should not be retried."""
    pass


class FileStore:
    def store_file(self, data_file:DataFile):
        # This should store the DataFile wherever is relevant for the implementing class
        # It should return the version_set information, which is a dictionary containing
        # a unique version key for the stored file, the md5 of the stored file, and the
        # files extension
        md5 = data_file.open_file.get_md5()
        return {
            'key': md5,
            'md5': md5,
            'extension': data_file.open_file.extension
        }

    def delete_file(self, path: str, version_id: str):
        pass

    def get_url(self, path: str, version_id: str, expiration: float):
        return ''

    @contextmanager
    def get_fileobj(self, path: str):
        try:
            fileobj = BytesIO()
            yield fileobj
        finally:
            fileobj.close()

    def get_file_size(self, path: str):
        return 0

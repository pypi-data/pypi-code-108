import os
from contextlib import contextmanager

from ocs_archive.storage.filestore import FileStore
from ocs_archive.input.file import DataFile
from ocs_archive.settings import settings

class FileSystemStore(FileStore):
    """This class stores the files locally on the file system, in the base directory specified.

    It does not support versioning of files, and will overwrite any file
    with the same path and filename. Please use S3 storage if you want versioning support.
    """
    def __init__(self, root_dir: str = settings.FILESYSTEM_STORAGE_ROOT_DIR):
        """Create filesystem storage manager using the root directory specified."""
        super().__init__()
        self.root_dir = root_dir

    def store_file(self, data_file: DataFile):
        md5 = data_file.open_file.get_md5()
        directory = os.path.join(self.root_dir, os.path.dirname(data_file.get_filestore_path()))
        os.makedirs(directory, exist_ok=True)  # ensure that the directory exists or make it
        with open(os.path.join(self.root_dir, data_file.get_filestore_path()), 'wb') as fp:
            fp.write(data_file.open_file.get_from_start().read())
        return {
            'key': md5,
            'md5': md5,
            'extension': data_file.open_file.extension
        }

    def delete_file(self, path: str, version_id: str):
        full_path = os.path.join(self.root_dir, path)
        if os.path.exists(full_path):
            os.remove(full_path)

    def get_url(self, path: str, version_id: str, expiration: float):
        # Filesystem storage files are assumed to be hosted at their base directory on the base url
        return os.path.join(settings.FILESYSTEM_STORAGE_BASE_URL, path)

    @contextmanager
    def get_fileobj(self, path: str):
        full_path = os.path.join(self.root_dir, path)
        fileobj = None
        try:
            if os.path.exists(full_path):
                fileobj = open(full_path, 'rb')
            yield fileobj
        finally:
            if fileobj:
                fileobj.close()

    def get_file_size(self, path: str):
        full_path = os.path.join(self.root_dir, path)
        return os.path.getsize(full_path)

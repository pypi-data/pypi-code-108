from ocs_archive.storage.filestore import FileStore, FileStoreSpecificationError
from ocs_archive.storage.filesystemstore import FileSystemStore
from ocs_archive.storage.s3store import S3Store
from ocs_archive.settings import settings


FILESTORE_TYPES_TO_CLASS = {
    'dummy': FileStore,
    'local': FileSystemStore,
    's3': S3Store
}


class FileStoreFactory:
    @staticmethod
    def get_file_store_class(filestore_type: str = settings.FILESTORE_TYPE):
        if filestore_type not in FILESTORE_TYPES_TO_CLASS:
            raise FileStoreSpecificationError(f'Invalid FileStore type {filestore_type}')
        return FILESTORE_TYPES_TO_CLASS[filestore_type]

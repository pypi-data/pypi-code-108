from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property

from security.config import settings


# File system storage
class BackupFileSystemStorage(FileSystemStorage):

    @cached_property
    def base_location(self):
        if not settings.BACKUP_STORAGE_PATH:
            raise ImproperlyConfigured('SECURITY_BACKUP_STORAGE_PATH settings is not set')
        return settings.BACKUP_STORAGE_PATH

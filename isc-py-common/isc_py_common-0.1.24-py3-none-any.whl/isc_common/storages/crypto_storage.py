import logging
import os
import shutil
from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.signals import setting_changed
from django.utils import timezone
from django.utils._os import safe_join
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri
from django.utils.functional import cached_property
from isc_common.common import SFTP, FILES_STORE_UNKNOWN_TYPE
from isc_common.oss.functions import get_tmp_dir

logger = logging.getLogger(__name__)


@deconstructible
class CryptoFileSystemStorage(Storage):

    def __init__(self, location=None, base_url=None, file_permissions_mode=None, directory_permissions_mode=None):
        self._location = location
        self._base_url = base_url
        self._file_permissions_mode = file_permissions_mode
        self._directory_permissions_mode = directory_permissions_mode
        setting_changed.connect(self._clear_cached_properties)

    def _clear_cached_properties(self, setting, **kwargs):
        """Reset setting based property values."""
        if setting == 'FILES_STORE':
            self.__dict__.pop('base_location', None)
            self.__dict__.pop('location', None)
        elif setting == 'MEDIA_URL':
            self.__dict__.pop('base_url', None)
        elif setting == 'FILE_UPLOAD_PERMISSIONS':
            self.__dict__.pop('file_permissions_mode', None)
        elif setting == 'FILE_UPLOAD_DIRECTORY_PERMISSIONS':
            self.__dict__.pop('directory_permissions_mode', None)

    def _value_or_setting(self, value, setting):
        return setting if value is None else value

    @cached_property
    def base_location(self):
        if isinstance(settings.FILES_STORE, str):
            file_store = settings.FILES_STORE
        elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
            file_store = get_tmp_dir()
        else:
            raise Exception(FILES_STORE_UNKNOWN_TYPE)

        return self._value_or_setting(self._location, file_store)

    @cached_property
    def location(self):
        return os.path.abspath(self.base_location)

    @cached_property
    def base_url(self):
        if self._base_url is not None and not self._base_url.endswith('/'):
            self._base_url += '/'
        return self._value_or_setting(self._base_url, settings.MEDIA_URL)

    @cached_property
    def file_permissions_mode(self):
        return self._value_or_setting(self._file_permissions_mode, settings.FILE_UPLOAD_PERMISSIONS)

    @cached_property
    def directory_permissions_mode(self):
        return self._value_or_setting(self._directory_permissions_mode, settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS)

    def _open(self, name, mode='rb'):
        return File(open(self.path(name), mode))

    def _save(self, name, content):
        full_path = self.path(name)

        if isinstance(settings.FILES_STORE, str):
            _dir, _filename = os.path.split(full_path)
            _filename1, _ = _filename.split('_')

            name = f'{os.path.abspath(settings.FILES_STORE)}{os.sep}{_filename}'

            shutil.copy2(src=f'{_dir}{os.sep}{_filename1}', dst=name)

            if self.file_permissions_mode is not None:
                os.chmod(name, self.file_permissions_mode)

        elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
            _dir, _filename = os.path.split(full_path)
            _filename1, _ = _filename.split('_')
            name = f'{settings.FILES_STORE.get("PATH")}{os.sep}{_filename}'
            localpath = f'{_dir}{os.sep}{_filename1}'

            ssh_client = settings.SSH_CLIENTS.client(settings.FILES_STORE)
            res = ssh_client.put(localpath=localpath, remotepath=name)
            if res is not None:
                raise res

            if self.file_permissions_mode is not None:
                ssh_client.chmod(path=name, mode=self.file_permissions_mode)
        else:
            raise Exception(FILES_STORE_UNKNOWN_TYPE)

        # Store filenames with forward slashes, even on Windows.
        return name.replace('\\', '/')

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        name = self.path(name)
        # If the file or directory exists, delete it from the filesystem.
        try:
            if os.path.isdir(name):
                os.rmdir(name)
            else:
                os.remove(name)
        except FileNotFoundError as e:
            raise e
            # logger.warning(f'{name}: not found.')

    def exists(self, name):
        return os.path.exists(self.path(name))

    def listdir(self, path):
        path = self.path(path)
        directories, files = [], []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                directories.append(entry)
            else:
                files.append(entry)
        return directories, files

    def path(self, name):
        return safe_join(self.location, name)

    def size(self, name):
        return os.path.getsize(self.path(name))

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip('/')
        return urljoin(self.base_url, url)

    def _datetime_from_timestamp(self, ts):
        if settings.USE_TZ:
            # Safe to use .replace() because UTC doesn't have DST
            return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(ts)

    def get_accessed_time(self, name):
        return self._datetime_from_timestamp(os.path.getatime(self.path(name)))

    def get_created_time(self, name):
        return self._datetime_from_timestamp(os.path.getctime(self.path(name)))

    def get_modified_time(self, name):
        return self._datetime_from_timestamp(os.path.getmtime(self.path(name)))

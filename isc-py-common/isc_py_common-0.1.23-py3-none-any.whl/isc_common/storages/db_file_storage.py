# python
import base64
import os

# third party
from django.core.files.base import ContentFile
from django.db.models import BinaryField
from django.utils.deconstruct import deconstructible
from django.utils.http import urlencode

# project
from isc_common import delete_drive_leter
from isc_common.storages.storage_ex import StorageEx


class NameException(Exception):
    pass


@deconstructible
class DatabaseFileStorage(StorageEx):
    """File storage system that saves models' FileFields in the database.
    Intended for use with Models' FileFields.
    Uses a specific model for each FileField of each Model.
    """

    NAME_FORMAT_HINT = '<app>.<model>/<content_field>/<filename_field>/<mimetype_field>/<filename>'
    NAME_FORMAT_HINT1 = '<app>.<model>/<content_field>/<filename_field>/<mimetype_field>'

    def _get_encoded_bytes_from_file(self, content_field, _file):
        _file.seek(0)
        file_content = _file.read()
        encoded = base64.b64encode(file_content)
        if isinstance(content_field, BinaryField):
            return encoded
        return encoded.decode('utf-8')

    def _get_file_from_encoded_bytes(self, encoded_bytes):
        file_buffer = base64.b64decode(encoded_bytes)
        return ContentFile(file_buffer)

    def _get_storage_attributes(self, name):
        try:
            (
                model_class_path,
                content_field,
                filename_field,
                mimetype_field,
                filename
            ) = name.split(os.sep, 4)
        except ValueError:
            raise NameException(
                'Wrong name format. Got {} ; should be {}'.format(name, self.NAME_FORMAT_HINT))

        filename = delete_drive_leter(filename)

        return {
            'model_class_path': model_class_path,
            'content_field': content_field,
            'filename_field': filename_field,
            'mimetype_field': mimetype_field,
            'filename': filename,
        }

    def _get_storage_attributes1(self, name):
        try:
            (
                model_class_path,
                content_field,
                filename_field,
                mimetype_field,
            ) = name.split(os.sep, 4)
        except ValueError:
            raise NameException(
                'Wrong name format. Got {} ; should be {}'.format(name, self.NAME_FORMAT_HINT1))

        return {
            'model_class_path': model_class_path,
            'content_field': content_field,
            'filename_field': filename_field,
            'mimetype_field': mimetype_field,
        }

    def _open(self, name, mode='rb'):
        assert mode[0] in 'rwab'

        if os.sep != '/':
            self.download_from = self.download_from.replace('/', os.sep)

        storage_attrs = self._get_storage_attributes1(self.download_from)
        model_class_path = storage_attrs['model_class_path']
        content_field = storage_attrs['content_field']
        filename_field = storage_attrs['filename_field']
        mimetype_field = storage_attrs['mimetype_field']
        filename = name

        model_cls = self._get_model_cls(model_class_path)
        model_instance = model_cls.objects.only(content_field, mimetype_field).get(**{filename_field: name})
        encoded_bytes = getattr(model_instance, content_field)

        _file = self._get_file_from_encoded_bytes(encoded_bytes)
        _file.filename = filename
        _file.mimetype = getattr(model_instance, mimetype_field)
        return _file

    def _save(self, name, content):
        storage_attrs = self._get_storage_attributes(name)
        model_class_path = storage_attrs['model_class_path']
        content_field_name = storage_attrs['content_field']
        filename_field_name = storage_attrs['filename_field']
        mimetype_field_name = storage_attrs['mimetype_field']

        model_cls = self._get_model_cls(model_class_path)
        new_filename = delete_drive_leter(content.file.name)

        content_field = model_cls._meta.get_field(content_field_name)
        encoded_bytes = self._get_encoded_bytes_from_file(content_field, content)

        mimetype = (
                getattr(content, 'content_type', None) or  # Django >= 1.11
                getattr(content.file, 'content_type', None) or  # Django < 1.11
                'application/octet-stream'  # Fallback
        )

        model_cls.objects.create(**{
            content_field_name: encoded_bytes,
            filename_field_name: new_filename,
            mimetype_field_name: mimetype,
        })
        return new_filename

    def delete(self, name):
        if os.sep != '/':  # Windows fix (see a6d4707) # pragma: no cover
            name = name.replace('/', os.sep)
        storage_attrs = self._get_storage_attributes(name)
        model_class_path = storage_attrs['model_class_path']
        filename_field = storage_attrs['filename_field']

        model_cls = self._get_model_cls(model_class_path)
        model_cls.objects.filter(**{filename_field: name}).delete()

    def exists(self, name):
        if os.sep != '/':  # Windows fix (see a6d4707) # pragma: no cover
            name = name.replace('/', os.sep)
        try:
            storage_attrs = self._get_storage_attributes(name)

        except NameException:
            return False

        model_class_path = storage_attrs['model_class_path']
        filename_field = storage_attrs['filename_field']

        model_cls = self._get_model_cls(model_class_path)
        return model_cls.objects.filter(**{filename_field: name}).exists()

    def url(self, name):
        return urlencode({'name': name})

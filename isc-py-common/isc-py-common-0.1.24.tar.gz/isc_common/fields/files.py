import os

from django.conf import settings
from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from isc_common.fields import Field


def FILE_ex(image, ssh_files):
    attfile = str(image.attfile)
    if attfile != '':
        _, _attfile = os.path.split(attfile)
        attfile = f'{settings.FILES_STORE.get("PATH")}{os.sep}{_attfile}'
        exist = ssh_files.exists(attfile)
        if exist is True:
            image.attfile = _attfile
            image.save()
        return exist, ssh_files.getsize(attfile)
    else:
        return False, 0


def make_REPLACE_FILE_PATH(name):
    if name == '':
        return name

    name = name.replace('\\', os.sep)
    replase_dir = None
    if isinstance(settings.REPLACE_FILE_PATH, dict):
        for key, value in settings.REPLACE_FILE_PATH.items():
            if replase_dir is not None and replase_dir != value:
                raise Exception('Несовпадение параметров замены')
            replase_dir = value
            name = name.replace(key, value)
    _, file_name = os.path.split(name)
    if replase_dir is not None:
        if replase_dir[-1:] != os.sep:
            replase_dir = replase_dir + os.sep
        name = f'{replase_dir}FILES{os.sep}{file_name}'
    return name


def make_REPLACE_IMAGE_PATH(full_name_image):
    full_name_image_replaced = full_name_image.replace(settings.PATH_IMAGES_REPLACE.get('old_path'), settings.PATH_IMAGES_REPLACE.get('new_path'))
    full_name_image_replaced = full_name_image_replaced.replace(os.altsep if os.altsep is not None else '\\', os.sep)
    return full_name_image_replaced


class FieldFileEx(FieldFile, Field):
    def get_replaced_name(self):
        self.name = make_REPLACE_FILE_PATH(name=self.name)
        return self.name

    def open(self, mode='rb'):
        self._require_file()
        if isinstance(settings.REPLACE_FILE_PATH, dict):
            for key, value in settings.REPLACE_FILE_PATH.items():
                self.name = self.name.replace(key, value)
        self.file = self.storage.open(self.name, mode)
        return self

    def save(self, name, content, save=True):
        name = os.path.abspath(name)
        _, file_name = os.path.split(self.storage.save(name, content, max_length=self.field.max_length))
        self.name = file_name
        setattr(self.instance, self.field.name, self.name)

        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()


class FileFieldEx(FileField):
    attr_class = FieldFileEx

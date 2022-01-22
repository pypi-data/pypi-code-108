from . import settings
from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string


class CustomStorageFileFieldMixin:
    def deconstruct(self):
        name, path, args, kwargs = super(CustomStorageFileFieldMixin, self).deconstruct()
        del kwargs['storage']
        return name, path, args, kwargs


class PublicFileFieldMixin(CustomStorageFileFieldMixin):
    description = "A FileField that uses a public storage option in production"

    def __init__(self, *args, **kwargs):
        kwargs['storage'] = import_string(settings.PUBLIC_FILE_STORAGE)
        super(PublicFileFieldMixin, self).__init__(*args, **kwargs)


class PrivateFileFieldMixin(CustomStorageFileFieldMixin):
    description = "A FileField that uses a private storage option in production"

    def __init__(self, *args, **kwargs):
        kwargs['storage'] = import_string(settings.PRIVATE_FILE_STORAGE)
        super(PrivateFileFieldMixin, self).__init__(*args, **kwargs)


class PublicFileField(PublicFileFieldMixin, models.FileField):
    pass


class PublicImageField(PublicFileFieldMixin, models.ImageField):
    pass


class PrivateFileField(PrivateFileFieldMixin, models.FileField):
    pass


class PrivateImageField(PrivateFileFieldMixin, models.ImageField):
    pass

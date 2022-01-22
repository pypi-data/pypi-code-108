from django.db import models

from kaos_storages.fields import PrivateFileField, PrivateImageField, PublicFileField, PublicImageField


def _assert_is_public(field):
    assert field.storage.__class__.__name__ == 'PublicMediaFilesS3Storage'
    assert field.storage.location == 'media'
    assert field.storage.default_acl == 'public-read'
    assert not field.storage.querystring_auth
    assert not field.storage.file_overwrite


def _assert_is_private(field):
    assert field.storage.__class__.__name__ == 'PrivateMediaFilesS3Storage'
    assert field.storage.location == 'private-media'
    assert field.storage.default_acl == 'private'
    assert field.storage.querystring_auth
    assert not field.storage.file_overwrite


def _assert_storage_deconstruct(field):
    name, path, args, kwargs = field.deconstruct()
    assert 'storage' not in kwargs


def test_PublicFileField():
    field = PublicFileField()

    _assert_is_public(field)
    _assert_storage_deconstruct(field)


def test_PublicImageField():
    field = PublicImageField()

    _assert_is_public(field)
    _assert_storage_deconstruct(field)


def test_PrivateFileField():
    field = PrivateFileField()

    _assert_is_private(field)
    _assert_storage_deconstruct(field)


def test_PrivateImageField():
    field = PrivateImageField()

    _assert_is_private(field)
    _assert_storage_deconstruct(field)


def test_default_public_file_storage(settings):
    settings.DEFAULT_FILE_STORAGE = 'kaos_storages.s3.PublicMediaFilesS3Storage'

    field = models.FileField()
    _assert_is_public(field)


def test_default_private_file_storage(settings):
    settings.DEFAULT_FILE_STORAGE = 'kaos_storages.s3.PrivateMediaFilesS3Storage'

    field = models.FileField()
    _assert_is_private(field)

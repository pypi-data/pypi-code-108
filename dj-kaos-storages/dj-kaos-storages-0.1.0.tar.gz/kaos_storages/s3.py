from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticFilesS3Storage(S3Boto3Storage):
    location = getattr(settings, 'STORAGES_STATICFILES_LOCATION', 'static')
    default_acl = 'public-read'
    querystring_auth = False


class PublicMediaFilesS3Storage(S3Boto3Storage):
    location = getattr(settings, 'STORAGES_PUBLIC_MEDIA_LOCATION', 'media')
    default_acl = 'public-read'
    querystring_auth = False
    file_overwrite = False


class PrivateMediaFilesS3Storage(S3Boto3Storage):
    location = getattr(settings, 'STORAGES_PRIVATE_MEDIA_LOCATION', 'private-media')
    default_acl = 'private'
    file_overwrite = False

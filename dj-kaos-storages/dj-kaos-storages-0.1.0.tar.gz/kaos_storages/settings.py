from django.conf import settings

if settings.DEBUG:
    settings.PUBLIC_FILE_STORAGE = getattr(settings, 'PUBLIC_FILE_STORAGE',
                                           'django.core.files.storage.FileSystemStorage')
    settings.PRIVATE_FILE_STORAGE = getattr(settings, 'PRIVATE_FILE_STORAGE',
                                            'django.core.files.storage.FileSystemStorage')

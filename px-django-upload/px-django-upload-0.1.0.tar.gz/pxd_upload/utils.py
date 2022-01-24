import os
from slugify import slugify


__all__ = (
    'filename_slugify',
    'filename_splitext',
)


def filename_slugify(string):
    return slugify(string)


def filename_splitext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)

    return name, ext

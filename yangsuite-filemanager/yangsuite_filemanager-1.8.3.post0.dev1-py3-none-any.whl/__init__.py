# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from yangsuite.paths import register_path
from ._version import get_versions

from .filemanager import (
    YSYangSet, YSMutableYangSet, YSYangDirectoryRepository, YSYangRepository,
    repository_path, yangset_path,
    merge_user_set, split_user_set,
    name_and_revision_from_file,
    list_yang_files, report_yang_files,
    atomic_create,
)

__version__ = get_versions()['version']
del get_versions

default_app_config = 'ysfilemanager.apps.YSFileManagerConfig'

register_path('scratch', 'scratch', parent='user', autocreate=True)
register_path('yangsets_dir', 'yangsets', parent='user', autocreate=True)
register_path('yangset', '{setname}', parent='yangsets_dir',
              autocreate=False, slugify=True)
register_path('repositories_dir', 'repositories', parent='user',
              autocreate=True)
register_path('repository', '{reponame}', parent='repositories_dir',
              autocreate=False, slugify=True)

__all__ = (
    'atomic_create',
    'list_yang_files',
    'merge_user_set',
    'name_and_revision_from_file',
    'report_yang_files',
    'repository_path',
    'split_user_set',
    'yangset_path',
    'YSYangSet',
    'YSMutableYangSet',
    'YSYangDirectoryRepository',
    'YSYangRepository',
)

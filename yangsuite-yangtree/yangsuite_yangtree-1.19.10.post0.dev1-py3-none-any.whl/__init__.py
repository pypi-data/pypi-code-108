# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from yangsuite.paths import register_path
from ._version import get_versions
from .context import YSContext
from .ymodels import YSYangModels, ParseYang

from .tasks import (
    TaskHandler,
    TaskException,
    set_replay_path,
    reset_replay_path,
    check_replays_subdir,
    check_default_replay_dir
)

__version__ = get_versions()['version']
del get_versions

# Additional storage paths defined by this package
register_path('testing_dir', 'testing', parent='user', autocreate=True)
register_path('replays_dir', 'replays', parent='testing_dir', autocreate=True)
register_path('replay_category_dir', '{category}', parent='replays_dir',
              autocreate=False, slugify=True)
register_path('replay_file', '{replay}.tsk', parent='replay_category_dir',
              autocreate=False, slugify=True)

# Deprecated - use 'replays_dir' instead
register_path('tasks_dir', 'replays', parent='testing_dir', autocreate=True)


default_app_config = 'ysyangtree.apps.YSYangTreeConfig'

__all__ = (
    'YSContext',
    'YSYangModels',
    'ParseYang',
    'TaskHandler',
    'TaskException',
    'set_replay_path',
    'reset_replay_path',
    'check_replays_subdir',
    'check_default_replay_dir'
)

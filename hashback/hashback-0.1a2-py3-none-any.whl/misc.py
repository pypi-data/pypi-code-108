import asyncio
import os

import appdirs
import collections.abc
import functools
import json
import logging
import signal
from copy import deepcopy
from pathlib import Path
from typing import Any, Collection, Coroutine, Dict, Optional, Union

logger = logging.getLogger(__name__)


def merge(base, update):
    base = deepcopy(base)
    for key, value in update.items():
        if isinstance(value, collections.abc.Mapping):
            base[key] = merge(base.get(key, {}), value)
        else:
            base[key] = value
    return base


def clean_shutdown(num, _):
    """
    Intended to be used as a signal handler
    """
    # pylint: disable=no-member
    logger.error(f"Caught signal '{signal.Signals(num).name}' - Shutting down")
    raise KeyboardInterrupt(f"Signal '{signal.Signals(num).name}'")


def run_then_cancel(future: Optional[Union[asyncio.Future, Coroutine]] = None,
                    loop: Optional[asyncio.BaseEventLoop] = None):
    if loop is None:
        loop = asyncio.get_event_loop()
    try:
        if future is None:
            return loop.run_forever()
        return loop.run_until_complete(future)
    finally:
        # There can still be running tasks on the event loop at this point.
        # Either 'future' has completed but other tasks on the loop have not, or some exception tripped us out of
        # running the loop.
        # Whatever the reason we want to cleanly cancel all remaining tasks (that's the point of this function).
        # To do that we MUST run the event loop after cancelling every task
        all_tasks = asyncio.all_tasks(loop)
        for task in all_tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*all_tasks, return_exceptions=True))


# pylint: disable=no-value-for-parameter
def register_clean_shutdown(numbers: Collection[Union[int, signal.Signals]] = (signal.SIGINT, signal.SIGTERM)):
    for num in numbers:
        signal.signal(num, clean_shutdown)


def str_exception(exception: Exception):
    return str(exception) or str(type(exception).__name__)


class SettingsConfig:
    APP_NAME = 'hashback'
    SETTINGS_FILE_DEFAULT_NAME: str = 'settings.json'

    @classmethod
    def customise_sources(cls, init_settings, env_settings, file_secret_settings):
        config_path = init_settings.init_kwargs.get('config_path', None)
        if config_path is None:
            # Try to find a default config.
            paths = [cls.user_config_path(), cls.site_config_path()]
            for possible_path in paths:
                if possible_path.exists():
                    config_path = possible_path
                    init_settings.init_kwargs['config_path'] = config_path
                    break

        if config_path is None:
            # There's no config file, even in a default location.  Initialize without any.
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )
        return (
            init_settings,
            functools.partial(cls._load_settings, config_path),
            env_settings,
            file_secret_settings,
        )

    @classmethod
    def user_config_path(cls) -> Path:
        return Path(appdirs.user_config_dir(cls.APP_NAME), cls.SETTINGS_FILE_DEFAULT_NAME)

    @classmethod
    def site_config_path(cls) -> Path:
        if 'XDG_CONFIG_DIRS' not in os.environ:
            os.environ['XDG_CONFIG_DIRS'] = '/etc'
            result = Path(appdirs.site_config_dir(cls.APP_NAME), cls.SETTINGS_FILE_DEFAULT_NAME)
            del os.environ['XDG_CONFIG_DIRS']
        else:
            result = Path(appdirs.site_config_dir(cls.APP_NAME), cls.SETTINGS_FILE_DEFAULT_NAME)
        return result

    @classmethod
    def _load_settings(cls, file_path: Path, _) -> Dict[str,Any]:
        try:
            with file_path.open('r') as settings_file:
                result = json.load(settings_file)
        except Exception as exc:
            logger.warning(f"Could not load {file_path}: ({str_exception(exc)}))")
            result = {}
        result['config_path'] = file_path
        return result


class ContextCloseMixin:

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

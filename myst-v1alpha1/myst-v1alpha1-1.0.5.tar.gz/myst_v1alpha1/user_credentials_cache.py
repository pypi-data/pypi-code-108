"""This module contains the `UserCredentialsCache` class."""
import errno
import logging
import os

from myst_v1alpha1.constants import MYST_CACHE_DIRNAME
from myst_v1alpha1.constants import MYST_USER_CREDENTIALS_FILENAME
from myst_v1alpha1.utils.cache_utils import get_local_app_config_path
from myst_v1alpha1.utils.cache_utils import load_user_credentials
from myst_v1alpha1.utils.cache_utils import save_user_credentials

logger = logging.getLogger(__name__)


class UserCredentialsCache(object):
    """User credentials cache class for saving and loading user credentials to a local cache.

    This writes user credentials to a subdirectory within the `~/.config` directory (or `APPDATA` on Windows).
    """

    def __init__(self, dirname=MYST_CACHE_DIRNAME, user_credentials_filename=MYST_USER_CREDENTIALS_FILENAME):
        """A `UserCredentialsCache` is optionally initialized with a cache subdirectory name and a user credentials
        cache filename.

        Args:
            dirname (str, optional): custom cache subdirectory name to override default one with
            user_credentials_filename (str): custom user credentials cache filename to override default one with
        """
        self._path = get_local_app_config_path(
            cache_dirname=dirname, user_credentials_filename=user_credentials_filename
        )

    def load(self):
        """Load credentials from cache.

        Returns:
            user_credentials (google.oauth2.credentials.Credentials or None): user credentials loaded from cache if we
                could not not load them for some reason (eg. they didn't exist, they were malformed, etc.)
        """
        try:
            user_credentials = load_user_credentials(user_credentials_path=self._path)
            return user_credentials
        except:
            logger.debug("Failed to load user credentials from cache.")

    def save(self, user_credentials):
        """Saves user credentials to cache.

        Args:
            user_credentials (google.oauth2.credentials.Credentials): user credentials to save to cache
        """
        return save_user_credentials(user_credentials=user_credentials, target_path=self._path)

    def clear(self):
        """Clears the user credentials cache."""
        try:
            os.remove(self._path)
        except OSError as error:
            if error.errno == errno.ENOENT:  # no such file or directory
                logger.debug("No user credentials cache to clear at path: '{path}'.".format(path=self._path))
            else:
                raise

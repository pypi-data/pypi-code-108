""" Utilities for loading modules/callables based on strings.
"""
import os
import re
import logging
import importlib
from typing import Callable
from sermos.constants import SERMOS_ACCESS_KEY, SERMOS_CLIENT_PKG_NAME

logger = logging.getLogger(__name__)


class SermosModuleLoader(object):
    """ Helper class to load modules / classes / methods based on a path string.
    """
    def get_module(self, resource_dot_path: str):
        """ Retrieve the module based on a 'resource dot path'.
            e.g. package.subdir.feature_file.MyCallable
        """
        module_path = '.'.join(resource_dot_path.split('.')[:-1])
        module = importlib.import_module(module_path)
        return module

    def get_callable_name(self, resource_dot_path: str) -> str:
        """ Retrieve the callable based on config string.
            e.g. package.subdir.feature_file.MyCallable
        """
        callable_name = resource_dot_path.split('.')[-1]
        return callable_name

    def get_callable(self, resource_dot_path: str) -> Callable:
        """ Retrieve the actual handler class based on config string.
            e.g. package.subdir.feature_file.MyCallable
        """
        module = self.get_module(resource_dot_path)
        callable_name = self.get_callable_name(resource_dot_path)
        return getattr(module, callable_name)


def normalized_pkg_name(pkg_name: str, dashed: bool = False):
    """ We maintain consistency by always specifying the package name as
        the "dashed version".

        Python/setuptools will replace "_" with "-" but resource_filename()
        expects the exact directory name, essentially. In order to keep it
        simple upstream and *always* provide package name as the dashed
        version, we do replacement here to 'normalize' both versions to
        whichever convention you need at the time.

        if `dashed`:
            my-package-name --> my-package-name
            my_package_name --> my-package-name

        else:
            my-package-name --> my_package_name
            my_package_name --> my_package_name
    """
    if dashed:
        return str(pkg_name).replace('_', '-')
    return str(pkg_name).replace('-', '_')


def get_client_pkg_name(pkg_name: str = None):
    """ Verify the package name provided and get from environment if None.

        Raise if neither provided nor found.

        Arguments:
          pkg_name (optional): Directory name for your Python
                    package. e.g. my_package_name . If none provided, will check
                    environment for `SERMOS_CLIENT_PKG_NAME`. If not found,
                    will exit.
    """
    pkg_name = pkg_name if pkg_name else SERMOS_CLIENT_PKG_NAME
    if pkg_name is None:
        msg = "Unable to find `pkg-name` in CLI arguments nor in "\
            "environment under `{}`".format('SERMOS_CLIENT_PKG_NAME')
        logger.error(msg)
        raise ValueError(msg)
    return pkg_name


def match_prefix(string: str, prefix_p: str) -> bool:
    """ For given string, determine whether it begins with provided prefix_p.
    """
    pattern = re.compile('^(' + prefix_p + ').*')
    if pattern.match(string):
        return True
    return False


def match_suffix(string: str, suffix_p: str) -> bool:
    """ For given string, determine whether it ends with provided suffix_p.
    """
    pattern = re.compile('.*(' + suffix_p + ')$')
    if pattern.match(string):
        return True
    return False


def match_prefix_suffix(string: str, prefix_p: str, suffix_p: str) -> bool:
    """ For given string, determine whether it starts w/ prefix & ends w/ suffix
    """
    if match_prefix(string, prefix_p) and match_suffix(string, suffix_p):
        return True
    return False


def find_from_environment(prefix_p: str, suffix_p: str) -> list:
    """ Find all envirionment variables that match prefix and suffix.

        Can provide any regex compatible string as values.
    """
    matching_vars = []
    environment_vars = os.environ
    for var in environment_vars:
        if match_prefix_suffix(var, prefix_p, suffix_p):
            matching_vars.append(var)
    return matching_vars

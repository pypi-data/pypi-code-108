"""Module with helpers for creating of the deployable components"""
import os
from askbot.deployment.exceptions import DeploymentError
from .manage_py import ManagePy
from .settings_py import SettingsPy
from .urls_py import UrlsPy

def get_root_path(path):
    """Returns root of the path, w/o the leading separator."""
    path_bits = path.split(os.path.sep)
    if ':' in path_bits[0]: #windows
        return path_bits[0] + os.path.sep
    return os.path.sep


def makedir(path, force):
    """Create a directory path.
    If path exists, and force is False, raise an exception.
    Otherwise force-create the directory/directories.
    Equivalent of mkdir -p
    """
    if os.path.exists(path) and not force:
        raise DeploymentError(f'Directory {path} exists')

    if force:
        path_bits = path.split(os.path.sep)
        existing_path = get_root_path(path)
        for path_bit in path.split(os.path.sep):
            if not path_bit:
                continue
            test_path = existing_path + path_bit + os.path.sep
            if not os.path.exists(test_path):
                os.makedirs(test_path)
            existing_path = test_path
    else:
        os.makedirs(path)

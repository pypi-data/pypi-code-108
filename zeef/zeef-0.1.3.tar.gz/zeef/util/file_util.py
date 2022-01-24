"""
    The file utils.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 16/12/2021
"""

import importlib.util
import pkg_resources
from pkg_resources import parse_version

MIN_TORCH_VERSION = '1.1.0'


def is_torch_available():
    return importlib.util.find_spec("torch") is not None


def check_torch_version():
    torch_version = pkg_resources.get_distribution('torch').version
    if parse_version(torch_version) < parse_version(MIN_TORCH_VERSION):
        msg = ('zeef depends on a newer version of PyTorch (at least {req}, not '
               '{installed}). Visit https://pytorch.org for installation details')
        raise ImportWarning(msg.format(req=MIN_TORCH_VERSION, installed=torch_version))

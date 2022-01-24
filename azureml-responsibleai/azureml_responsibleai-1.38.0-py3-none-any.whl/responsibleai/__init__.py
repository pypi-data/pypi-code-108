# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""azureml.responsibleai sub-package."""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore

try:
    from ._version import SELF_VERSION
    __version__ = SELF_VERSION
except ImportError:
    __version__ = '0.0.0+dev'

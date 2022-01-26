import sys
from distutils.version import LooseVersion

import distributed

from ._version import get_versions

COILED_VERSION = get_versions()["version"]

PY_VERSION = LooseVersion(".".join(map(str, sys.version_info[:3])))

DISTRIBUTED_VERSION = LooseVersion(distributed.__version__)

# -*- coding: utf-8 -*-
#! python3  # noqa E265

"""This module is an abstraction class about the Isogeo REST API.

https://www.isogeo.com/
"""

# submodules
from .__about__ import __version__  # noqa: F401
from .api_hooks import IsogeoHooks  # noqa: F401
from .checker import IsogeoChecker  # noqa: F401
from .decorators import ApiDecorators  # noqa: F401
from .exceptions import AlreadyExistError  # noqa: F401
from .isogeo import Isogeo  # noqa: F401
from .translator import IsogeoTranslator  # noqa: F401
from .utils import IsogeoUtils  # noqa: F401

# subpackages
from .api import *  # noqa: F401 F403
from .enums import *  # noqa: F401 F403
from .models import *  # noqa: F401 F403

VERSION = __version__

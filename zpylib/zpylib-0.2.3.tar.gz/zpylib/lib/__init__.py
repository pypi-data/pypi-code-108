from .lib import Lib

from .__builtin__ import BUILT_IN
from .standard import STANDARD
from .requests import REQUESTS

lib = Lib(BUILT_IN)

lib.use(STANDARD).use(REQUESTS)




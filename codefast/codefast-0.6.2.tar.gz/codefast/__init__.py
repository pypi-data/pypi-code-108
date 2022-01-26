import builtins
import sys

import codefast.reader
import codefast.utils as utils
from codefast.ds import fplist, nstr, pair_sample
from codefast._io import JoblibDiskCaching as jdc
from codefast.logger import Logger
from codefast.math import math
from codefast.utils import FileIO as io
from codefast.utils import FormatPrint as fp
from codefast.utils import b64decode, b64encode, cipher, decipher
from codefast.utils import json_io as js
from codefast.utils import retry, shell, uuid, syscall
from codefast.network import urljoin

# Export methods and variables
file = utils.FileIO
csv = utils.CSVIO
net = utils.Network
os = utils._os()

logger = Logger()
info = logger.info
error = logger.error
warning = logger.warning

say = io.say

# Deprecated
builtins.io = utils.FileIO
builtins.read = utils.FileIO()
builtins.jsn = utils.JsonIO()
json = utils.JsonIO()
text = utils.FileIO
sys.modules[__name__] = utils.wrap_mod(
    sys.modules[__name__],
    deprecated=['text', 'json', 'file', 'read', 'say', 'jsn'])

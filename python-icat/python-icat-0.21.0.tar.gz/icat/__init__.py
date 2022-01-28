"""Python interface to ICAT and IDS

This package provides a collection of modules for writing Python
programs that access an `ICAT`_ service using the SOAP interface.  It
is based on Suds and extends it with ICAT specific features.

.. _ICAT: https://icatproject.org/
"""

import sys
import warnings

if sys.version_info < (3, 4):
    warnings.warn("Support for Python versions older then 3.4 is deprecated  "
                  "and will be removed in python-icat 1.0", DeprecationWarning)

__version__ = "0.21.0"

#
# Default import
#

from icat.client import *
from icat.exception import *


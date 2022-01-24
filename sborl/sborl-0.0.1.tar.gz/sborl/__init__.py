"""Library for managing Juju interfaces based on schemas.
"""

__version__ = "0.0.1"

# flake8: noqa: F401,F402

from . import errors
from . import events
from . import relation
from .relation import EndpointWrapper
from . import testing

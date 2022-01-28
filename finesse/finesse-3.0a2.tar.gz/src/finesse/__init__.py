# flake8: noqa

"""Finesse is a Python package for simulating interferometers in the frequency
domain."""

import sys
import locale


PROGRAM = __name__
DESCRIPTION = "Simulation program for laser interferometers."

# Set the locale to the user's default (required for e.g. number formatting in log
# warnings).
locale.setlocale(locale.LC_ALL, "")

# Set the Finesse version.
try:
    from .version import version as __version__
except ImportError:
    raise Exception("Could not find version.py. Ensure you have run setup.")

# Set up some sensible default runtime options.
from .config import configure, autoconfigure

autoconfigure()

# Import a bunch of useful functions and classes into the top-level package.
from .env import (
    is_interactive,
    show_tracebacks,
    tb,
    session_instance as _session_instance,
)
from .constants import values as constants
from .parameter import Parameter, float_parameter
from .gaussian import BeamParam
from .model import Model
from .plotting import init as init_plotting
from .script import syntax, help_ as help
from .script import syntax

# Set up the user session.
session = _session_instance()

from .utilities.storage import save, load

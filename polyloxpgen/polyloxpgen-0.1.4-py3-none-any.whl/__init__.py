
"""polyloxpgen - Barcode purging and pgen (probability of generation) calculation for Polylox data."""

__version__ = '0.1.4'
__author__ = 'Maurice Langhinrichs <m.langhinrichs@icloud.com>'

# __all__ applies to importing with "from polyloxpgen import *"
__all__ = ['merge', 'pgen']

# to be able to use "import polyloxpgen" and "polyloxpgen.polylox_merge()":
from .merge import polylox_merge
from .pgen import polylox_pgen

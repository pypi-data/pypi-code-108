# read version from installed package
from importlib.metadata import version
__version__ = version("chemcalculator")

# populate package namespace
from chemcalculator.chemcalculator import compute_mass
from chemcalculator.chemcalculator import moles_grams_converter
from chemcalculator.chemcalculator import percent_mass

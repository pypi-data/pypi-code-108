from quickstats._version import __version__
from quickstats.decorators import *

import os
import pathlib

import ROOT
ROOT.gROOT.SetBatch(True) 
ROOT.PyConfig.IgnoreCommandLineOptions = True
module_path = pathlib.Path(__file__).parent.absolute()
macro_path = module_path
stylesheet_path = os.path.join(module_path, 'stylesheets')

# ROOT.gInterpreter.AddIncludePath(os.path.join(macro_path, "macros"))

MAX_WORKERS = 8

from quickstats.utils.io import VerbosePrint

_PRINT_ = VerbosePrint("INFO")

from quickstats.main import *

from quickstats.components.asimov_generator import AsimovType

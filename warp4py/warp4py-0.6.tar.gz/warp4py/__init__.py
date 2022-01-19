import sys

if sys.version_info <= (3,0):
  raise ImportError("Must use python3")

from ._model      import Model
from ._structure  import Structure
from ._material   import Material
from ._load       import NodalLoad
from ._load       import StepLoad
from ._load       import Constraint
from ._list       import GeometricList
from ._parameters import SolutionParameters
from ._parameters import CrackGrowthParameters

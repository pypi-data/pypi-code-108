from enum import Enum
from typing import Dict, Union

from origin.arithmetic import ArithmeticDict


TEmissionValue = Union[int, float]


class EmissionLabel(Enum):
    """
    System-wide labels of known emission types.
    """
    CO2 = 'CO2'
    SO2 = 'SO2'


class EmissionValues(ArithmeticDict, Dict[EmissionLabel, TEmissionValue]):
    """
    Represents a set of emissions indexed by label.

    Units of values depends on the context of their use (gram, gram/Wh, etc).
    """
    pass

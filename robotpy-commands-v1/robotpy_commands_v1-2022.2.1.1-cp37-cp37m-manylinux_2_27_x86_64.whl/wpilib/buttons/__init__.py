import warnings

warnings.warn(
    "wpilib.buttons has moved to commands1.buttons", FutureWarning, stacklevel=2
)

from commands1.buttons import *

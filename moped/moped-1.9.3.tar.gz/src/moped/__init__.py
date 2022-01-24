from __future__ import annotations

import logging
import os

from . import topological
from .core.compound import Compound
from .core.kinetic_data import KineticData
from .core.model import Model
from .core.monomer import Monomer
from .core.reaction import Reaction

__all__ = [
    "topological",
    "Compound",
    "KineticData",
    "Model",
    "Monomer",
    "Reaction",
]

logger = logging.getLogger("moped")
logger.setLevel(logging.WARNING)
formatter = logging.Formatter(
    fmt="{asctime} - {levelname} - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

os.environ["LC_ALL"] = "C"  # meneco bugfix

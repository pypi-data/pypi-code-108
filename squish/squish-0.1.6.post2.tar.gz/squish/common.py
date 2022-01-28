from __future__ import annotations
from typing import List, Tuple, Union, Optional, Iterator, Generator
import pickle, numpy as np
from math import gcd
from pathlib import Path
from squish.voronoi import VoronoiContainer
from squish.energy import AreaEnergy, RadialALEnergy, RadialTEnergy

OUTPUT_DIR = Path("squish_output")

STR_TO_ENERGY = {
    "area": AreaEnergy,
    "radial-al": RadialALEnergy,
    "radial-t": RadialTEnergy,
}


def generate_filepath(
    sim: SimulationMode, fol: Union[str, Path], prec: int = 2
) -> Path:
    energy = sim.energy.title_str
    width, height = round(sim.domain.w, prec), round(sim.domain.h, prec)

    base_path = (
        f"{fol}/{energy}{sim.title_str} - "
        + f"N{sim.domain.n} - {width:.{prec}f}x{height:.{prec}f}"
    )

    i = 1
    real_path = Path(base_path)
    while real_path.is_dir():
        real_path = Path(f"{base_path}({i})")
        i += 1

    return real_path


class DomainParams:
    """Container for basic domain parameters

    Attributes:
        n (int): Number of sites in simulation.
        w (float): width of the bounding domain.
        h (float): height of the bounding domain.
        r (float): natural radius of the objects.
        dim (np.ndarray): dimensions, w x h.

    """

    __slots__ = ["n", "w", "h", "r", "dim"]

    def __init__(self, n: int, w: float, h: float, r: float) -> None:
        if n < 2:
            raise ValueError("Number of objects should be larger than 2!")

        if w <= 0:
            raise ValueError("Width needs to be nonzero and positive!")

        if h <= 0:
            raise ValueError("Height needs to be nonzero and positive!")

        self.n, self.w, self.h, self.r = int(n), float(w), float(h), float(r)
        self.dim = np.array([self.w, self.h])

    def __iter__(self) -> Iterator:
        return iter((self.n, self.w, self.h, self.r))

    def __str__(self) -> str:
        return f"N = {self.n}, R = {self.r}, {self.w} X {self.h}"


class Energy:
    """Generic container for energies.

    Attributes:
        mode (VoronoiContainer): VoronoiContainer for the chosen energy.

    """

    __slots__ = ["mode"]

    def __init__(self, mode: Union[str, VoronoiContainer]) -> None:
        if isinstance(mode, str):
            try:
                self.mode = STR_TO_ENERGY[mode.lower()]
            except KeyError:
                raise ValueError(f"'{mode}' is not a valid energy!")
        else:
            if mode is not VoronoiContainer and issubclass(mode, VoronoiContainer):
                raise ValueError("Provided class is not a valid energy!")
            self.mode = mode

    @property
    def attr_str(self) -> str:
        return self.mode.attr_str

    @property
    def title_str(self) -> str:
        return self.mode.title_str

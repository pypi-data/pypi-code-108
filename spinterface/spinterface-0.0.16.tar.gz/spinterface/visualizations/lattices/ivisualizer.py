# -*- coding: utf-8 -*-
r"""
Module contains abstract base class for visualizing spin structures / lattices.
"""
from abc import ABC, abstractmethod
from spinterface.inputs.lattice.ILattice import ILattice
from pathlib import Path


class IVisualizer(ABC):
    r"""
    Abstract class for visualizations of spin structures
    """

    def __init__(self, lattice: ILattice) -> None:
        r"""
        Initialization method for the visualizer. Will be called from sub class

        Args:
            lattice(ILattice): realization of ILattice
        """
        self.lattice = lattice

    @abstractmethod
    def __call__(self, outpath: Path = Path.cwd() / 'lattice.png'):
        r"""
        Call method for the visualization

        Args:
            outpath(Path): path for the output file
        """

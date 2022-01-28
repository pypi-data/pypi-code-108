# -*- coding: utf-8 -*-
r"""
Class for the hexagonal lattice. Stacked in the aa stacking order. All atoms sit on the same lattice sites.
"""
from povray.states_pyvista.ILattice import ILattice
from povray.states_pyvista.CCubicLattice import CCubicLatticeStackAA
import numpy as np
import povray.states_pyvista.utilities as utils
import pyvista as pv
from typing import List
import matplotlib


class CHexLatticeStackAA(ILattice):
    r"""
    Number of hexagonal lattices stacked directly above each other. This means that a3||e_z.
    """

    def __init__(self, ip_lattconst: float = 1, oop_lattconst: float = 1, N1: int = 50, N2: int = 50,
                 N3: int = 1, magdir: np.ndarray = np.array([0.0, 0.0, 1.0]), magmom: float = 1.0) -> None:
        r"""
        Initializes the lattice

        Args:
            ip_lattconst(float): in plane lattice constant
            oop_lattconst(float): out of plane lattice constant
            N1(int): number of unit cells in a1 dir.
            N2(int): number of unit cells in a2 dir.
            N3(int): number of unit cells in a2 dir.
            magdir(array): initial direction of the magnetization
            magmom(float): magnetic moment of lattice
        """
        a1 = np.array([0.5, np.sqrt(3) / 2, 0]) * ip_lattconst
        a2 = np.array([0.5, -np.sqrt(3) / 2, 0]) * ip_lattconst
        a3 = np.array([0, 0, 1]) * oop_lattconst
        super().__init__(a1=a1, a2=a2, a3=a3, N1=N1, N2=N2, N3=N3, magdir=magdir, magmom=magmom)

    def add_skyrmiontube(self, vorticity: int = 1.0, helicity: float = np.pi / 1, c: float = 2.5, w: float = 2.0,
                         AFM: bool = False) -> None:
        r"""
        Adds a skyrmion tube in all layers. Each layer has the same skyrmion (same parameters). Does also works for
        monolayer skyrmions

        Args:
            vorticity(int): topological charge of the skyrmion
            helicity(float): pi -> neel, pi/2 -> bloch
            c(float): size of the domain in the middle of the skyrmion
            w(float): size of the region where the spins tilt (domain wall width)
            AFM(bool): whether each layer shall be antiferromagnet
        """
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            XY = magstructure_layer[:, :2].copy() - self.layermidpoints[layer][:2]
            r = np.linalg.norm(XY, axis=1)
            pp = np.arctan2(XY[:, 1], XY[:, 0])
            th = utils.theta(r, c, w)
            ph = utils.phi(pp, vorticity, helicity)
            n = np.arange(0, len(XY[:, 0]), 1)
            if AFM:
                sign = (-1) ** (n % 2 + n // int(np.sqrt(len(XY[:, 0]))))
            else:
                sign = 1
            uplo = 1
            magstructure_layer[:, 3] = np.sin(th) * np.cos(ph) * sign
            magstructure_layer[:, 4] = np.sin(th) * np.sin(ph) * sign
            magstructure_layer[:, 5] = np.cos(th) * float(uplo) * sign
            self.setlayer_by_idx(layer, magstructure_layer)

    def add_SAF_skyrmiontube(self, vorticity: int = 1.0, helicity: float = np.pi / 1, c: float = 2.5, w: float = 3.0,
                             AFM: bool = False) -> None:
        r"""
        Adds a synthethic antiferromagnetic skyrmion tube in all layers. Each layer has the same skyrmion
        (same parameters). Does also works for monolayer skyrmions

        Args:
            vorticity(int): topological charge of the skyrmion
            helicity(float): pi -> neel, pi/2 -> bloch
            c(float): size of the domain in the middle of the skyrmion
            w(float): size of the region where the spins tilt (domain wall width)
            AFM(bool): whether each layer shall be antiferromagnet
        """
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            XY = magstructure_layer[:, :2].copy() - self.layermidpoints[layer][:2]
            r = np.linalg.norm(XY, axis=1)
            pp = np.arctan2(XY[:, 1], XY[:, 0])
            th = utils.theta(r, c, w)
            ph = utils.phi(pp, vorticity, helicity)
            n = np.arange(0, len(XY[:, 0]), 1)
            if AFM:
                sign = (-1) ** (n % 2 + n // int(np.sqrt(len(XY[:, 0]))))
            else:
                sign = 1
            uplo = 1
            magstructure_layer[:, 3] = np.sin(th) * np.cos(ph) * sign
            magstructure_layer[:, 4] = np.sin(th) * np.sin(ph) * sign
            magstructure_layer[:, 5] = np.cos(th) * float(uplo) * sign
            if layer % 2 == 0:
                magstructure_layer[:, 3:6] = magstructure_layer[:, 3:6] * -1
            self.setlayer_by_idx(layer, magstructure_layer)

    def add_chiralbobber(self, vorticity: int = 1.0, helicity: float = np.pi / 1, c: List[float] = [0.0, 1.0, 1.5, 2.5],
                         w: List[float] = [0.0, 1.5, 2.0, 3.0],
                         AFM: bool = False) -> None:
        r"""
        Adds a skyrmion tube in all layers. Each layer has the same skyrmion (same parameters). Does also works for
        monolayer skyrmions

        Args:
            vorticity(int): topological charge of the skyrmion
            helicity(float): pi -> neel, pi/2 -> bloch
            c(float): size of the domain in the middle of the skyrmion
            w(float): size of the region where the spins tilt (domain wall width)
            AFM(bool): whether each layer shall be antiferromagnet
        """
        for layer in range(self.nlayer):
            magstructure_layer = self.getlayer_by_idx(layer)
            if layer >= len(c) or c[layer] == 0.0:
                continue
            XY = magstructure_layer[:, :2].copy() - self.layermidpoints[layer][:2]
            r = np.linalg.norm(XY, axis=1)
            pp = np.arctan2(XY[:, 1], XY[:, 0])
            th = utils.theta(r, c[layer], w[layer])
            ph = utils.phi(pp, vorticity, helicity)
            n = np.arange(0, len(XY[:, 0]), 1)
            if AFM:
                sign = (-1) ** (n % 2 + n // int(np.sqrt(len(XY[:, 0]))))
            else:
                sign = 1
            uplo = 1
            magstructure_layer[:, 3] = np.sin(th) * np.cos(ph) * sign
            magstructure_layer[:, 4] = np.sin(th) * np.sin(ph) * sign
            magstructure_layer[:, 5] = np.cos(th) * float(uplo) * sign
            self.setlayer_by_idx(layer, magstructure_layer)

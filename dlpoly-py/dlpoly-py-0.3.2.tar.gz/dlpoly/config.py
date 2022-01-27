"""
Module to handle DLPOLY config files
"""

import copy
import numpy as np

# from dlpoly-py.species import Species
from .utility import DLPData


class Atom(DLPData):
    """ Class defining a DLPOLY atom type

     :param element: Label
     :param pos: Position vector
     :param vel: Velocity vector
     :param forces: Net force vector
     :param index: ID

     """

    def __init__(self, element="", pos=None, vel=None, forces=None, index=1):
        DLPData.__init__(
            self,
            {
                "element": str,
                "pos": (float, float, float),
                "vel": (float, float, float),
                "forces": (float, float, float),
                "index": int,
                "molecule": (str, int),
            },
        )
        self.element = element
        self.pos = np.zeros(3) if pos is None else pos
        self.vel = np.zeros(3) if vel is None else vel
        self.forces = np.zeros(3) if forces is None else forces
        self.index = index

    def write(self, level):
        """ Print own data to file w.r.t config print level

        :param level: Print level ; 1 = Pos, 2 = Vel, 3 = Forces

        """
        if level == 0:
            return "{:8s}{:10d}\n{:20.10f}" "{:20.10f}{:20.10f}".format(
                self.element, self.index, *self.pos
            )

        if level == 1:
            return (
                "{:8s}{:10d}\n"
                "{:20.10f}{:20.10f}{:20.10f}\n"
                "{:20.10f}{:20.10f}{:20.10f}"
            ).format(self.element, self.index, *self.pos, *self.vel)
        if level == 2:
            return (
                "{:8s}{:10d}\n"
                "{:20.10f}{:20.10f}{:20.10f}\n"
                "{:20.10f}{:20.10f}{:20.10f}\n"
                "{:20.10f}{:20.10f}{:20.10f}"
            ).format(self.element, self.index, *self.pos, *self.vel, *self.forces)
        raise ValueError(f"Invalid print level {level} in Config.write")

    def __str__(self):
        return (
            "{:8s}{:10d}\n"
            "{:20.10f}{:20.10f}{:20.10f}\n"
            "{:20.10f}{:20.10f}{:20.10f}\n"
            "{:20.10f}{:20.10f}{:20.10f}\n"
        ).format(self.element, self.index, *self.pos, *self.vel, *self.forces)

    def read(self, fileHandle, level, i):
        """ Reads info for one atom

        :param fileHandle: File to read
        :param level: Level to readd
        :param i: Index

        """
        line = fileHandle.readline()
        if not line:
            return False
        ei = line.split()
        if len(ei) == 1:
            self.element = ei[0]
            # there is no index in the file, we shall ignore
            # probably breaking hell loose somewhere else
            self.index = i
        if len(ei) == 2:
            self.element = ei[0]
            self.index = int(ei[1])
        self.pos = [float(i) for i in fileHandle.readline().split()]
        if level > 0:
            self.vel = [float(i) for i in fileHandle.readline().split()]
            if level > 1:
                self.forces = [float(i) for i in fileHandle.readline().split()]
        return self


class Config:
    """ Class defining a DLPOLY config file

     :param source: File to read

     """

    params = {
        "atoms": list,
        "cell": np.ndarray,
        "pbc": int,
        "natoms": int,
        "level": int,
        "title": str,
    }

    natoms = property(lambda self: len(self.atoms))

    def __init__(self, source=None):
        self.title = ""
        self.level = 0
        self.atoms = []
        self.pbc = 0
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.source = source
            self.read(source)

    def write(self, filename="new.config", title=None, level=0):
        """ Output to file

        :param filename: File to write
        :param title: Title of run
        :param level: Print level ; 1 = Pos, 2 = Vel, 3 = Forces

        """
        self.level = level
        with open(filename, "w") as outFile:
            outFile.write("{0:72s}\n".format(self.title if title is None else title))
            outFile.write(
                "{0:10d}{1:10d}{2:10d}\n".format(level, self.pbc, self.natoms)
            )
            if self.pbc > 0:
                for j in range(3):
                    outFile.write(
                        "{0:20.10f}{1:20.10f}{2:20.10f}\n".format(
                            self.cell[j, 0], self.cell[j, 1], self.cell[j, 2]
                        )
                    )
            for atom in self.atoms:
                print(atom.write(self.level), file=outFile)

    def add_atoms(self, other):
        """ Add two Configs together to make one bigger config

        :param other: Config to add

        """
        lastIndex = self.natoms
        if isinstance(other, Config):
            self.atoms += [copy.copy(atom) for atom in other.atoms]
        elif isinstance(other, (list, tuple)):
            self.atoms += [copy.copy(atom) for atom in other]
        # Shift new atoms' indices to reflect place in new config
        for i in range(lastIndex, self.natoms):
            self.atoms[i].index += lastIndex

    def read(self, filename="CONFIG"):
        """ Read file into Config

        :param filename: Filt to read

        """
        try:
            fileIn = open(filename, "r")
        except IOError:
            print("File {0:s} does not exist!".format(filename))
            return []

        self.title = fileIn.readline().strip()
        line = fileIn.readline().split()
        self.level = int(line[0])
        self.pbc = int(line[1])
        if self.pbc > 0:
            for j in range(3):
                line = fileIn.readline().split()
                for i in range(3):
                    try:
                        self.cell[j, i] = float(line[i])
                    except ValueError:
                        raise RuntimeError("Error reading cell")

        self.atoms = []
        i = 0
        while True:
            i += 1
            atom = Atom().read(fileIn, self.level, i)
            if not atom:
                break
            self.atoms.append(atom)

        fileIn.close()
        return self


if __name__ == "__main__":
    CONFIG = Config().read()
    CONFIG.write()

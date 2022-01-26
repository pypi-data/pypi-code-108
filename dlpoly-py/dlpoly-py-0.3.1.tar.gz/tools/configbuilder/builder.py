"""
Code to build CONFIG/FIELD from layound files
"""

import copy
import random
import numpy as np
from dlpoly.field import Field
from dlpoly.config import Config
from dlpoly.utility import parse_line, read_line
from .cfgLoader import CFG


class System:
    """ System to run """
    keywords = ("cell", "include", "potential")

    def __init__(self):
        self.config = Config()
        self.config.level = 0
        self.field = Field()
        self.CFGs = {}

        self.defined = {key: False for key in System.keywords}

    def handle_structure(self, source):
        """ Read a structure block and add each element to the system

        :param source: Source file to parse

        """
        lastConfig = None
        while True:
            line = read_line(source)
            line = parse_line(line)
            while line.endswith("&"):
                line += read_line(source).strip("&")
            if line.lower() == "end structure":
                break

            keyword, *args = line.split()
            keyword = keyword.lower()

            if keyword == "include":
                filename, *args = args
                if filename not in self.CFGs:
                    self.CFGs[filename] = CFG(filename)

                lastConfig = self._add_config(self.CFGs[filename], args)

            elif keyword == "lattice":
                if self.config.level == 0:
                    raise ValueError("Cannot generate lattice with no cell specified")

                shape, *args = args

                if shape in ("cubic",):
                    spacing, *args = args

            elif keyword == "repeat":
                nRepeat, *args = args
                for i in range(int(nRepeat)):
                    lastConfig = self._add_config(lastConfig, args[:])
        print(self.field.molecules["Water molecule"].nMols)

    def _add_config(self, inConfig, args):
        """ Add a config to the current system
        Returns: Last Config
        """
        newConfig = copy.copy(inConfig)

        currMol = self.field.add_molecule(newConfig)
        for atom in newConfig.atoms:
            atom.molecule = currMol

        while args:
            keyword = args.pop(0).lower()
            if keyword == "angle":
                alpha, beta, gamma, *args = args
                angle = tuple(ang if ang != "rand" else random.uniform(0, 180.)
                              for ang in (alpha, beta, gamma))
                newConfig.rotate(np.asarray(angle, dtype=float))
            elif keyword == "pos":
                x, y, z, *args = args
                newConfig.translate(np.asarray((x, y, z), dtype=float))
            elif keyword == "stretch":
                x, y, z, *args = args
                newConfig.stretch(np.asarray((x, y, z), dtype=float))
            else:
                raise IOError("Unrecognised keyword {} in {}".format(keyword, "include"))

        if "replace" in args:
            newConfig.clear_config(newConfig)

        self.config.add_atoms(newConfig.atoms)
        return newConfig

    def _del_config(self, delMol):
        """ Delete a configuration from system """
        molName, molID = delMol
        fieldMol = self.field.molecules[molName]
        fieldMol.nMols -= 1
        if not fieldMol.nMols:
            del self.field.molecules[molName]

        self.config.atoms = [atom for atom in self.config.atoms
                             if atom.molecule != delMol]

    def _clear_config(self, config, radius=1.):
        """ Clear the space occupied by a molecule
        determined by deleting any molecules in a cylindrical radius around defined internal bonding

        :param config: Configuration to check space of
        :param radius: Radius in Angstroms of cylinders
        """

        radiusSq = radius**2

        # Calculate current list of potential conflicts
        potentialConflicts = [atom for atom in self.config.atoms
                              if any(atom.pos > config.bounds[0]-radius and
                                     atom.pos < config.bounds[1]+radius)]

        for constraintClass in ("bonds", "constraints", "rigid"):
            for pot in config.get_pot_by_class(constraintClass):
                atomi, atomj = config.atoms[pot.atoms[0]], config.atoms[pot.atoms[1]]
                rij = atomj.pos - atomi.pos
                modRijSq = np.dot(rij, rij)

                for trialAtom in potentialConflicts:
                    riPt = trialAtom.pos - atomi.pos
                    dot = np.dot(riPt, rij)
                    if 0.0 < dot < modRijSq and np.dot(riPt, riPt) - dot**2/modRijSq < radiusSq:
                        # delete molecule!
                        self._del_config(trialAtom.molecule)

    def handle_cell(self, line):
        """ Read a cell line and set corresponding pbcs

        :param line: Lines to read

        """
        key, *args = line.split()
        if self.defined["cell"]:
            raise ValueError("{} multiply defined in {}".format(key.capitalize(), line))
        self.config.cell = np.zeros((3, 3))
        if len(args) == 1:  # Fill diagonal
            for i in range(3):
                self.config.cell[i, i] = args[0]
            self.config.pbc = 1
        elif len(args) == 3:  # Assume diagonal
            for i in range(3):
                self.config.cell[i, i] = args[i]
            self.config.pbc = 2
        elif len(args) == 9:  # Full matrix
            self.config.cell = np.asarray(args).reshape((3, 3))
            self.config.pbc = 3
        else:
            raise IOError("Cannot handle cell line: {}".format(line))

    def handle_potential_block(self, source):
        """ Read a potential block into the field

        :param source: Source file

        """
        for line in source:
            if line.lower() == "end potential":
                break
            line = parse_line(line)
            potClass, nPots = line.split()
            nPots = int(nPots)
            self.field._read_block(source, potClass, nPots)
        else:
            raise IOError("Unended potential block")


def build(source):
    """Construct a structure

    :param source: Source file to read
    :returns: Parsed system

    """
    system = System()
    for line in source:
        line = parse_line(line).lower()
        if not line:
            continue
        key, *args = line.split()

        if key == "structure":
            system.handle_structure(source)
        elif key == "cell":
            system.handle_cell(line)
        elif key == "potential":
            system.handle_potential_block(source)

    return system

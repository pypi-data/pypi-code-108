'''
Module containing data relating to DLPOLY field files
'''

from collections import defaultdict
from abc import ABC
from .species import Species
from .utility import read_line, peek


class Interaction(ABC):
    ''' Abstract base class for managing atomic interactions '''
    def __init__(self):
        self._potClass = None

    nAtoms = {}

    @property
    def potClass(self):
        ''' The type of potential '''
        return self._potClass

    @potClass.setter
    def potClass(self, potClass):
        if potClass not in self.potClasses:
            raise IOError('Unrecognised {} class {}. Must be one of {}'.format(type(self).__name__, potClass,
                                                                               ', '.join(self.potClasses)))
        self._potClass = potClass

    potClasses = property(lambda self: [potClass for potClass in self.nAtoms.keys()])


class Bond(Interaction):
    ''' Class containing information regarding bonds in molecules '''
    nAtoms = {'atoms': 1, 'bonds': 2, 'constraints': 2, 'angles': 3, 'dihedrals': 4, 'inversions': 4, 'rigid': -1}

    def __init__(self, potClass=None, params=None):
        Interaction.__init__(self)
        self.potClass = potClass
        # In bonds key comes first...
        self.potType, params = params[0], params[1:]
        self.atoms, self.params = params[0:self.nAtoms[potClass]], params[self.nAtoms[potClass]:]

    def __str__(self):
        return '{} {} {}'.format(self.potType, ' '.join(self.atoms), ' '.join(self.params))


class Potential(Interaction):
    ''' Class containing information regarding potentials '''
    nAtoms = {'extern': 0, 'vdw': 2, 'metal': 2, 'rdf': 2, 'tbp': 3, 'fbp': 4}

    def __init__(self, potClass=None, params=None):
        Interaction.__init__(self)
        self.potClass = potClass
        # In potentials atoms come first...
        self.atoms, params = params[0:self.nAtoms[potClass]], params[self.nAtoms[potClass]:]
        self.potType, self.params = params[0], params[1:]
        if params is not None:
            # Atoms always in alphabetical/numerical order
            self.atoms = sorted(self.atoms)

    def __str__(self):
        return '{} {} {}'.format(' '.join(self.atoms), self.potType, ' '.join(self.params))


class PotHaver(ABC):
    ''' Abstract base class defining an object which contains potentials or bonds '''
    def __init__(self):
        self.pots = defaultdict(list)

    def add_potential(self, atoms, potential):
        ''' Add a potential to the list of available potentials '''
        if not isinstance(potential, (Potential, Bond)):
            raise TypeError('Tried to add non-potential to a potential containing object')

        self.pots[tuple(atoms)].append(potential)

    def set_potential(self, oldPot, newPot):
        ''' Override a potential with a new one '''
        for i, currPot in enumerate(self.pots[oldPot.atoms]):
            if currPot == oldPot:
                self.pots[oldPot.atoms][i] = newPot
                return

    def get_pot(self, species=None, potClass=None, potType=None, quiet=False):
        ''' Return all pots for a given pot type '''

        tests = (('atoms', species), ('potClass', potClass), ('potType', potType))
        out = peek(pot for potSet in self.pots.values() for pot in potSet if
                   all(getattr(pot, prop) == val for prop, val in tests if val is not None)
                   )
        if out is None:
            if quiet:
                for name, val in tests:
                    if val is not None:
                        print('No potentials for {} {} found'.format(name, val))
            out = ()
        return out

    def get_pot_by_species(self, species, quiet=False):
        ''' Return all pots for a given pot species '''
        return self.get_pot(species=species, quiet=quiet)

    def get_pot_by_class(self, potClass, quiet=False):
        ''' Return all pots for a given pot class '''
        return self.get_pot(potClass=potClass, quiet=quiet)

    def get_pot_by_type(self, potType, quiet=False):
        ''' Return all pots for a given pot type '''
        return self.get_pot(potType=potType, quiet=quiet)

    def get_num_pot_by_species(self, species, quiet=False):
        ''' Return all pots for a given pot species '''
        return len(list(self.get_pot_by_species(species, quiet)))

    def get_num_pot_by_class(self, potClass, quiet=False):
        ''' Return all pots for a given pot class '''
        return len(list(self.get_pot_by_class(potClass, quiet)))

    def get_num_pot_by_type(self, potType, quiet=False):
        ''' Return all pots for a given pot type '''
        return len(list(self.get_pot_by_type(potType, quiet)))


class Molecule(PotHaver):
    ''' Class containing field molecule data '''
    def __init__(self):
        PotHaver.__init__(self)
        self.name = ''
        self.nMols = 0
        self.nAtoms = 0
        self.species = {}

    activeBonds = property(lambda self: (name for name in Bond.nAtoms if self.get_num_pot_by_class(name)))

    def read(self, fieldFile):
        ''' Read a single molecule into class and return itself '''
        self.name = read_line(fieldFile).strip()
        self.nMols = int(read_line(fieldFile).split()[1])
        line = read_line(fieldFile)
        while line.lower() != 'finish':
            potClass, nPots = line.split()
            potClass = potClass.lower()
            nPots = int(nPots)
            self._read_block(fieldFile, potClass, nPots)
            line = read_line(fieldFile)
        return self

    def get_masses(self):
        masses = []
        for s in self.species.keys():
            masses += [self.species[s].mass] * self.species[s].repeats
        return masses

    def get_charges(self):
        charges = []
        for s in self.species.keys():
            charges += [self.species[s].charge] * self.species[s].repeats
        return charges

    def write(self, outFile):
        ''' Write self to outFile (called by Field) '''
        print(self.name, file=outFile)
        print('nummols {}'.format(self.nMols), file=outFile)
        print('atoms {}'.format(self.nAtoms), file=outFile)
        for element in self.species.values():
            print(element, file=outFile)

        for potClass in self.activeBonds:
            pots = list(self.get_pot_by_class(potClass))
            print('{} {}'.format(potClass, len(pots)), file=outFile)
            for pot in pots:
                print(pot, file=outFile)
        print('finish', file=outFile)

    def _read_block(self, fieldFile, potClass, nPots):
        ''' Read a potentials block '''
        if potClass.lower() == 'atoms':
            self.nAtoms = nPots
            self._read_atoms(fieldFile, nPots)
            return

        for pot in range(nPots):
            args = read_line(fieldFile).split()
            pot = Bond(potClass, args)
            self.add_potential(pot.atoms, pot)

    def _read_atoms(self, fieldFile, nAtoms):
        atom = 0
        index = 0
        while atom < nAtoms:
            name, weight, charge, *repeatsFrozen = read_line(fieldFile).split()
            if repeatsFrozen:
                repeats, frozen, *_ = repeatsFrozen
            else:
                repeats, frozen = 1, 0
            repeats = int(repeats)
            self.species[index] = Species(name, len(self.species), charge, weight, frozen, repeats)
            atom += repeats
            index += 1


class Field(PotHaver):
    ''' Class containing field data '''

    def __init__(self, source=None):
        PotHaver.__init__(self)
        self.header = ''
        self.units = 'internal'
        self.molecules = {}
        if source is not None:
            self.source = source
            self.read(self.source)

    vdws = property(lambda self: list(self.get_pot_by_class('vdw')))
    metals = property(lambda self: list(self.get_pot_by_class('metal')))
    rdfs = property(lambda self: list(self.get_pot_by_class('rdf')))
    tersoffs = property(lambda self: list(self.get_pot_by_class('tersoff')))
    tbps = property(lambda self: list(self.get_pot_by_class('tbp')))
    fbps = property(lambda self: list(self.get_pot_by_class('fbp')))
    externs = property(lambda self: list(self.get_pot_by_class('extern')))

    nMolecules = property(lambda self: len(self.molecules))
    nVdws = property(lambda self: len(self.vdws))
    nMetals = property(lambda self: len(self.metals))
    nRdfs = property(lambda self: len(self.rdfs))
    nTersoffs = property(lambda self: len(self.tersoffs))
    nTbps = property(lambda self: len(self.tbps))
    nFbps = property(lambda self: len(self.fbps))
    nExterns = property(lambda self: len(self.externs))

    activePots = property(lambda self: (name for name in Potential.nAtoms if self.get_num_pot_by_class(name)))
    species = property(lambda self: {spec.element: spec
                                     for mol in self.molecules.values()
                                     for spec in mol.species.values()})
    potSpecies = property(lambda self: {spec for specPairs in self.pots for spec in specPairs})

    def _read_block(self, fieldFile, potClass, nPots):
        ''' Read a potentials block '''
        if potClass == 'tersoff':
            self._read_tersoff(fieldFile, nPots)
            return
        for pot in range(nPots):
            args = fieldFile.readline().split()
            pot = Potential(potClass, args)
            self.add_potential(pot.atoms, pot)

    def _read_tersoff(self, fieldFile, nPots):
        ''' Read a tersoff set (different to standard block) '''

    def add_molecule(self, molecule):
        ''' Add molecule to self '''
        if molecule.name not in self.molecules:
            self.molecules[molecule.name] = molecule
        self.molecules[molecule.name].nMols += 1

        return molecule.name, self.molecules[molecule.name].nMols

    def read(self, fieldFile='FIELD'):
        ''' Read field file into data '''
        with open(fieldFile, 'r') as inFile:
            # Header *must* be first line?
            self.header = inFile.readline().strip()
            key, self.units = read_line(inFile).split()
            line = read_line(inFile)
            while line.lower() != 'close':
                key, *nVals = line.lower().split()
                nVals = int(nVals[-1])
                if key.startswith('molecul'):
                    for _ in range(nVals):
                        mol = Molecule().read(inFile)
                        self.molecules[mol.name] = mol
                else:
                    self._read_block(inFile, key, nVals)
                line = read_line(inFile)

    def write(self, fieldFile='FIELD'):
        ''' Write data to field file '''
        with open(fieldFile, 'w') as outFile:
            print(self.header, file=outFile)
            print('units {}'.format(self.units), file=outFile)
            print('molecules {}'.format(self.nMolecules), file=outFile)
            for molecule in self.molecules.values():
                molecule.write(outFile)
            for potClass in self.activePots:
                pots = list(self.get_pot_by_class(potClass, quiet=True))
                print('{} {}'.format(potClass, len(pots)), file=outFile)
                for pot in pots:
                    print(pot, file=outFile)
            print('close', file=outFile)


if __name__ == '__main__':
    FLD = Field('FIELD')
    FLD.write('geoff')

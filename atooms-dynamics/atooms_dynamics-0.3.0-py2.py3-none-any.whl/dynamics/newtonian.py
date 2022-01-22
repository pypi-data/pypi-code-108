#!/usr/bin/env python
# This file is part of atooms
# Copyright 2010-2014, Daniele Coslovich

"""Molecular dynamics fortran backend for atooms"""

import os
import math
import numpy
import logging

from atooms.core.utils import Timer

_log = logging.getLogger(__name__)


class MolecularDynamicsBase(object):

    def __init__(self, system, timestep=0.001):
        self.system = system
        self.verlet_list = None

        # Add unfolded position to particles
        # They are initialized as the folded positions
        for p in self.system.particle:
            p.position_unfolded = p.position.copy()
        self.initial = system.__class__()
        self.initial.update(self.system, exclude=['interaction'])
        # Clear existing views on position_unfolded
        # self.system.dump('particle.position_unfolded', clear=True)
        if self.system._data is not None and \
           'particle.position_unfolded' in self.system._data:
            del(self.system._data['particle.position_unfolded'])

        # Molecular dynamics specific stuff
        self.conserved_energy = 0.0
        self.timestep = timestep

        # We compute the initial potential energy
        self.system.compute_interaction('forces')
        self._reference_energy = None

        # Timers
        self._timer = {
            'dump': Timer(),
            'evolve': Timer(),
            'forces': Timer()
        }

    def __str__(self):
        txt = """
backend: newtonian dynamics
algorithm: {}
timestep: {}
""".format(self.__class__, self.timestep)
        return txt

    @property
    def rmsd(self):
        current = self.system.dump('particle.position_unfolded', order='F', view=True)
        initial = self.initial.dump('particle.position_unfolded', order='F', view=True)
        msd = numpy.sum((current - initial)**2) / len(self.system.particle)
        return msd**0.5

    def run(self):
        # Implement this
        pass


class VelocityVerlet(MolecularDynamicsBase):

    def run(self, steps):
        # Dump the arrays before we start. This can be done at each
        # run() call because we ask for views, and this does not incur
        # into overhead.
        self._timer['dump'].start()
        _box = self.system.dump('cell.side', dtype='float64', view=True)
        _pos = self.system.dump('particle.position', dtype='float64', order='F', view=True)
        _vel = self.system.dump('particle.velocity', dtype='float64', order='F', view=True)
        _ids = self.system.dump('particle.species', dtype='int32', view=True)
        _rad = self.system.dump('particle.radius', dtype='float64', view=True)
        _pos_unf = self.system.dump('particle.position_unfolded', order='F', view=True)
        # Masses have to be replicated along the spatial dimensions to keep the vector syntax
        # The None indexing syntax adds a new dimension to the array
        _mas = self.system.dump('particle.mass', dtype='float64', view=True)
        _mas = numpy.repeat(_mas[:, numpy.newaxis], len(_box), axis=1)
        _mas = numpy.transpose(_mas, (1, 0))
        if self._reference_energy is None:
            self._reference_energy = self.system.total_energy()

        # Build f90 kernel module if necessary
        import f2py_jit
        uid = f2py_jit.build_module(os.path.join(os.path.dirname(__file__), 'kernels_soft.f90'))
        f90 = f2py_jit.import_module(uid)
        self._timer['dump'].stop()

        # Main loop
        for _ in range(steps):
            self._timer['evolve'].start()
            f90.methods.evolve_velocity_verlet(1,
                                               self.timestep,
                                               self.system.interaction.forces,
                                               _box,
                                               _pos,
                                               _pos_unf,
                                               _vel,
                                               _ids,
                                               _mas)
            self._timer['evolve'].stop()
            self._timer['forces'].start()
            self.system.compute_interaction('forces')
            self._timer['forces'].stop()
            self._timer['evolve'].start()
            f90.methods.evolve_velocity_verlet(2,
                                               self.timestep,
                                               self.system.interaction.forces,
                                               _box,
                                               _pos,
                                               _pos_unf,
                                               _vel,
                                               _ids,
                                               _mas)
            self._timer['evolve'].stop()

        self.conserved_energy = self.system.total_energy(cache=True) - self._reference_energy


class NosePoincare(MolecularDynamicsBase):

    def run(self, steps):
        # Dump the arrays before we start. This can be done at each
        # run() call because we ask for views, and this does not incur
        # into overhead.
        self._timer['dump'].start()
        _box = self.system.dump('cell.side', dtype='float64', view=True)
        _pos = self.system.dump('particle.position', dtype='float64', order='F', view=True)
        _vel = self.system.dump('particle.velocity', dtype='float64', order='F', view=True)
        _ids = self.system.dump('particle.species', dtype='int32', view=True)
        _rad = self.system.dump('particle.radius', dtype='float64', view=True)
        _pos_unf = self.system.dump('particle.position_unfolded', order='F', view=True)
        # Masses have to be replicated along the spatial dimensions to keep the vector syntax
        # The None indexing syntax adds a new dimension to the array
        _mas = self.system.dump('particle.mass', dtype='float64', view=True)
        _mas = numpy.repeat(_mas[:, numpy.newaxis], len(_box), axis=1)
        _mas = numpy.transpose(_mas, (1, 0))
        # Make sure the thermostat coordinates are 0-dim arrays
        # TODO: this calls for coords/moms to be added to Thermostat
        thermostat = self.system.thermostat
        # Reference energy
        ndim = self.system.number_of_dimensions
        ndf = ndim * (len(self.system.particle) - 1)
        if self._reference_energy is None:
            thermostat = self.system.thermostat
            # TODO: this calls for a NosePoincareThermostat.energy method?
            self._reference_energy = self.system.total_energy() + \
                thermostat.momentum**2 / (2*thermostat.mass) + \
                ndf * thermostat.temperature * math.log(thermostat.coordinate)

        # Build f90 kernel module if necessary
        import f2py_jit
        uid = f2py_jit.build_module(os.path.join(os.path.dirname(__file__), 'kernels_soft.f90'))
        f90 = f2py_jit.import_module(uid)
        self._timer['dump'].stop()

        # Main loop
        for _ in range(steps):
            self._timer['evolve'].start()
            f90.methods.evolve_nose_poincare(1,
                                             self.timestep,
                                             self.system.interaction.forces,
                                             0.0, 0.0,
                                             thermostat.temperature,
                                             thermostat.coordinate,
                                             thermostat.momentum,
                                             thermostat.mass,
                                             self._reference_energy,
                                             _box,
                                             _pos,
                                             _pos_unf,
                                             _vel,
                                             _ids,
                                             _mas)
            self._timer['evolve'].stop()
            self._timer['forces'].start()
            epot_old = self.system.interaction.energy
            self.system.compute_interaction('forces')
            epot_new = self.system.interaction.energy
            self._timer['forces'].stop()
            self._timer['evolve'].start()
            f90.methods.evolve_nose_poincare(2,
                                             self.timestep,
                                             self.system.interaction.forces,
                                             epot_old, epot_new,
                                             thermostat.temperature,
                                             thermostat.coordinate,
                                             thermostat.momentum,
                                             thermostat.mass,
                                             self._reference_energy,
                                             _box,
                                             _pos,
                                             _pos_unf,
                                             _vel,
                                             _ids,
                                             _mas)
            self._timer['evolve'].stop()

        energy = self.system.total_energy(cache=True) + \
            thermostat.momentum**2 / (2*thermostat.mass) + \
            ndf * thermostat.temperature * math.log(thermostat.coordinate)
        self.conserved_energy = thermostat.coordinate * (energy - self._reference_energy)


class EventDrivenAllenTildesley:

    def __init__(self, system, timestep=0.001):
        self.system = system
        self.timestep = timestep
        self._init = False

    def __str__(self):
        txt = """
backend: event driven molecular dynamics
algorithm: allen-tildesley
timestep: {}
""".format(self.timestep)
        return txt

    @property
    def rmsd(self):
        return 0.0

    def run(self, steps):
        # Build f90 kernel module
        import f2py_jit
        path = os.path.join(os.path.dirname(__file__), 'kernels_hard.f90')
        f90 = f2py_jit.jit(path)
        # Inlining with 0.6.0 gives a seg fault
        # f90 = f2py_jit.jit(f2py_jit.inline(path))  #, extra_args='--opt="-fbounds-check"')

        # Dump variables
        box = self.system.dump('cell.side', view=True)
        pos = self.system.dump('particle.position', order='F', view=True)
        vel = self.system.dump('particle.velocity', order='F', view=True)
        ids = self.system.dump('particle.species', dtype='int32', view=True)
        rad = self.system.dump('particle.radius', view=True)
        if not self._init:
            self._coltime = numpy.ndarray(len(self.system.particle))
            self._partner = numpy.ndarray(len(self.system.particle), dtype='int32')
            f90.methods.run(pos, vel, rad*2, box[0], self.timestep, 0, self._coltime, self._partner)
            self._init = True

        # Main loop
        f90.methods.run(pos, vel, rad*2, box[0], self.timestep, steps, self._coltime, self._partner)


EventDriven = EventDrivenAllenTildesley

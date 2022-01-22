#!/usr/bin/env python
# This file is part of atooms
# Copyright 2010-2014, Daniele Coslovich

"""Stochastic dynamics fortran backend for atooms"""

import os
import math
import numpy
import copy
import logging

from atooms.core.utils import Timer
from .helpers import mean_square_displacement

_log = logging.getLogger(__name__)


class LangevinOverdamped(object):

    def __init__(self, system, timestep=0.001, friction=1.0,
                 temperature=1.0, fixed_cm=True, random=None):
        self.system = system
        self.verlet_list = None
        self.fixed_cm = fixed_cm
        self.random = numpy.random if random is None else random

        # TODO: refactor
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

        # Langevin dynamics specific stuff
        self.timestep = timestep
        self.friction = friction
        self.temperature = temperature
        self._D = temperature / friction
        self._width = (2 * self._D * timestep)**0.5,

        # We compute the initial potential energy
        self.system.compute_interaction('forces')

        # Timers
        self.timer = {
            'dump': Timer(),
            'evolve': Timer(),
            'forces': Timer()
        }

    def __str__(self):
        txt = """
backend: stochastic dynamics
algorithm: overdamped Langevin
timestep: {}
friction: {}
temperature: {}
random: {}
""".format(self.timestep, self.friction, self.temperature, self.random)
        return txt

    @property
    def rmsd(self):
        current = self.system.dump('particle.position_unfolded', order='F', view=True)
        initial = self.initial.dump('particle.position_unfolded', order='F', view=True)
        msd = numpy.sum((current - initial)**2) / len(self.system.particle)
        return msd**0.5

    def run(self, steps):
        # Dump views of the arrays before we start
        # TODO: if order changes the view is not updated
        self.timer['dump'].start()
        _box = self.system.dump('cell.side', dtype='float64', view=True)
        _pos = self.system.dump('particle.position', dtype='float64', view=True, order='F')
        _ids = self.system.dump('particle.species', dtype='int32', view=True)
        _rad = self.system.dump('particle.radius', dtype='float64', view=True)
        _pos_unf = self.system.dump('particle.position_unfolded', view=True, order='F')
        import f2py_jit
        uid = f2py_jit.build_module(os.path.join(os.path.dirname(__file__), 'kernels_soft.f90'))
        f90 = f2py_jit.import_module(uid)
        self.timer['dump'].stop()

        # Main loop
        for _ in range(steps):
            self.timer['forces'].start()
            self.system.compute_interaction('forces')
            self.timer['forces'].stop()
            # Overdamped Langevin dynamics
            self.timer['evolve'].start()
            noise = self.random.normal(0.0, self._width, _pos.shape)
            noise = numpy.asfortranarray(noise)
            delta = noise + self.system.interaction.forces * self.timestep / self.friction

            # Subtract CM motion
            if self.fixed_cm:
                f90.methods.fix_cm(delta)

            # Update positions
            _pos += delta
            _pos_unf += delta
            f90.methods.pbc(_pos, _box, _box / 2)
            self.timer['evolve'].stop()

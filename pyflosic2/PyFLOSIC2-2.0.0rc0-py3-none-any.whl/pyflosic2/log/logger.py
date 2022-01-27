#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
import numpy
import scipy
import datetime
import ase
import pyscf
try:
    import distro
except BaseException:
    print('Python package distro not installed!')

import sys
from pyflosic2.version.version import code_name


class logger:
    """
        Logger class for PyFLOSIC2
        - screen output : stdout
        - f_log : log-file name
    """

    def __init__(self, f_log='stdout'):
        self.f_log = f_log
        if self.f_log == 'stdout':
            self.f = sys.stdout
        if self.f_log != 'stdout':
            # SS: buffering = 1 -> only one line buffer
            f = open(self.f_log, 'w', buffering=1)
            self.f = f
        # Code and version header
        self.write(code_name)
        # Write system and code information
        self.print_time()
        self.print_versions()
        self.print_distro()

    def print_time(self):
        """
            Print: time
            -----------
        """
        now = datetime.datetime.now()
        self.header('Time: {}'.format(now.strftime("%Y-%m-%d %H:%M")))

    def print_versions(self):
        """
            Print: package versions
            -----------------------
        """
        self.header('Used packages versions:')
        try:
            self.write('numpy : %s' % (numpy.__version__))
        except BaseException:
            self.write('Python package numpy not installed!')
        try:
            self.write('scipy : %s' % (scipy.__version__))
        except BaseException:
            self.write('Python package scipy not installed!')
        try:
            self.write('ase   : %s' % (ase.__version__))
        except BaseException:
            self.write('Python package ase not installed!')
        try:
            self.write('pyscf : %s' % (pyscf.__version__))
        except BaseException:
            self.write('Python package pyscf not installed!')

    def print_distro(self):
        """
            Print: OS
            ---------
        """
        try:
            dst = distro.linux_distribution()
            self.header('OS: {} {} {}'.format(dst[0], dst[1], dst[2]))
        except BaseException:
            self.write('Python package distro not installed!')

    def write(self, msg):
        """
            Write >> msg << to log-file

            msg  : Str()
        """
        self.f.write(msg + '\n')

    def info(self, msg):
        """
            Write >> date (time): msg << to log-file

            msg  : Str()
        """
        now = datetime.datetime.now()
        # dd/mm/YY (H:M:S):
        dt_string = now.strftime("%d/%m/%Y (%H:%M:%S):")
        self.f.write("{} {} \n".format(dt_string, msg))

    def header(self, task):
        """
            Write task as caption (format with box)

            task : Str()
        """
        str_msg = " {} ".format(task)
        layout = "-" * len(str_msg)
        self.f.write(layout + "\n")
        self.f.write(str_msg + "\n")
        self.f.write(layout + "\n")

    def init_task(self, task, msg, infos=None):
        """
            Write [start] of a task with
            a msg and optional infos

            task : Str()
            msg  : Str()
            infos: List(Str(),Str(),...]
        """
        str_msg = " [Start] {} : {}".format(task, msg)
        layout = "-" * len(str_msg)
        self.f.write(layout + "\n")
        self.f.write(str_msg + "\n")
        self.f.write(layout + "\n")
        if infos is not None:
            for i in infos:
                self.f.write(" - {}\n".format(i))

    def end_task(self, task, msg, infos=None):
        """
            Write [end] of a task with
            a msg and optional infos

            task : Str()
            msg  : Str()
            infos: List(Str(),Str(),...]
        """
        str_msg = " [End]   {} : {}".format(task, msg)
        layout = "-" * len(str_msg)
        self.f.write(layout + "\n")
        self.f.write(str_msg + "\n")
        self.f.write(layout + "\n")
        if infos is not None:
            for i in infos:
                self.f.write(" - {}\n".format(i))

    def close(self):
        """
            Close log-file
        """
        if self.f_log != 'stdout':
            self.f.close()

    def __del__(self):
        """
            Destructor?
            If logger instance is destroyed also
            the log-file is destroyed.
        """
        self.close()

    def print_xyz(self, atoms):
        """
            Write xyz
            -----------
            Write FLO-SIC xyz to xyz file

            Input
            -----
        """
        natoms = len(atoms)
        self.write('{:d}'.format(natoms))
        if atoms._elec_symbols[1] is not None:
            self.write("sym_fod1='{}' sym_fod2='{}'".format(atoms._elec_symbols[0], atoms._elec_symbols[1]))
        if atoms._elec_symbols[1] is None:
            self.write("sym_fod1='{}'".format(atoms._elec_symbols[0]))
        for s, (x, y, z) in zip(atoms.symbols, atoms.positions):
            self.write('{:2s} {:22.15f} {:22.15f} {:22.15f}'.format(s, x, y, z))


if __name__ == '__main__':
    from pyflosic2.parameters.flosic_parameters import parameters
    p = parameters()
    p.log.write('Test')
    p.log.info('A is bigger than B')
    p.log = logger('pyflosic2.log')
    p.log.init_task('Calculate Something', 'Lets go')
    p.log.end_task('Calculate Something', 'Lets go', ['Amazing results.', 'Snow is cold.'])
    l = [[1, 1, 1], [2, 2, 2]]
    a = numpy.array(l)
    p.log.write(str(l))
    p.log.write(str(a))

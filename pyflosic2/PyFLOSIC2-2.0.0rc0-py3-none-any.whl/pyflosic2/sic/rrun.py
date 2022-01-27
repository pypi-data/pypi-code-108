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
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.sic.rworkflow import RWORKFLOW
from pyflosic2.systems.rflosic_systems import CH4
from pyflosic2.io.flosic_io import atoms2flosic

class RRUN(RWORKFLOW):
    """
        The RRUN class
        --------------
        Similar to RWORKFLOW, however the input contains now
        both nuclei and initial FODs. Thus

            atoms = nuclei + fod1 

        This routine can be used if FODs are generated with
        different FOD generators, e.g., pyfodmc.
    """

    def __init__(self, atoms, **kwargs):
        """
            Initialize class
            ----------------

            Input
            -----
            - system information
                atoms: atoms, nuclei and FODs
                spin: int(), 2S = Nalpha - Nbeta, spin
                charge: int(), charge of the system
            - calculation information
                sym_fod1: str(), symbol FODs
                tier_name: str(), default numerical parameter levels, e.g., 'tier1'
                flevel: int(), FLO-SIC approximation (0-3), (low - high accuracy)
                log_name: str(), output log file name
        """
        # _atoms = nuclei + fod1 
        self._atoms = atoms
        [nuclei,fod1,_] = atoms2flosic(atoms,
                                       sym_fod1=atoms._elec_symbols[0],
                                       sym_fod2=atoms._elec_symbols[1])
        super().__init__(atoms=nuclei,**kwargs)

    def guess(self):
        """
            Get: FOD guess
            --------------
        """
        # We have already the guess, i.e., 
        #   _atoms = nuclei + fod1  
        self.p.atoms = self._atoms
        self.p.log.write('FOD guess given as input.')

if __name__ == '__main__':
    from pyflosic2.test.knight_valley.rrun.test_rrun import test_rrun

    test_rrun()

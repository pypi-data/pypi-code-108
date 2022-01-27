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
from pyflosic2.sic.uworkflow import UWORKFLOW
from pyflosic2.sic.rworkflow import RWORKFLOW


def WORKFLOW(atoms,
             tier_name='tier1',
             flevel=0,
             log_name='pyflosic2.log',
             mode='unrestricted'):
    """ 
    
        PyFLOSIC2: WORKFLOW 
        
        Workflow to run FLO-SIC 
        from nuclei only information, i.e., chemical symbols and positions.
        The initial Fermi-orbital descriptors (FODs) are generated 
        within the workflow. 

        Parameters
        ----------
            atoms: Atoms()
                Atoms object/instance 
            tier_name: str()
                Tier name 
            flevel: int()
                0-3 FLO-SIC levels
            log_name: str()
                logging file name 
            mode: str()
                'unrestricted' or 'restricted'

        Examples
        --------

	>>> from pyflosic2 import Atoms, WORKFLOW
	>>> # Nuclei
	>>> sym = ['C']+4*['H']
	>>> p0 = [+0.00000000,+0.00000000,+0.00000000]
	>>> p1 = [+0.62912000,+0.62912000,+0.62912000]
	>>> p2 = [-0.62912000,-0.62912000,+0.62912000]
	>>> p3 = [+0.62912000,-0.62912000,-0.62912000]
	>>> p4 = [-0.62912000,+0.62912000,-0.62912000]
	>>> pos = [p0,p1,p2,p3,p4]
	>>> atoms = Atoms(sym,pos,spin=0,charge=0)
	>>> # Workflow
	>>> wf = WORKFLOW(atoms,
        >>>               tier_name='tier1',
        >>>               flevel=0,
        >>>               log_name='UWF.log',
        >>>               mode='unrestricted')
	>>> wf.kernel()
	>>> print(wf.p.atoms,wf.etot)



    """
    if mode == 'unrestricted':
        return UWORKFLOW(atoms=atoms,
                         tier_name=tier_name,
                         flevel=flevel,
                         log_name=log_name)
    if mode == 'restricted':
        return RWORKFLOW(atoms=atoms,
                         tier_name=tier_name,
                         flevel=flevel,
                         log_name=log_name)


if __name__ == '__main__':
    from pyflosic2.test.knight_valley.workflow.test_workflow import test_workflow

    test_workflow()

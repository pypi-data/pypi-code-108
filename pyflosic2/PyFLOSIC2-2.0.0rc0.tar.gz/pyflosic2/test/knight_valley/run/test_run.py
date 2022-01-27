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
from pyflosic2 import Atoms, RUN
from pyflosic2.systems.uflosic_systems import CH4 as uatoms
from pyflosic2.systems.rflosic_systems import CH4 as ratoms

def test_run():
    # Unrestricted workflow
    uwf = RUN(uatoms(), mode='unrestricted',log_name='URUN.log')
    # FLO-SIC approximations
    uwf.kernel(update=False, flevel=0)
    uwf.kernel(update=False, flevel=1)
    uwf.kernel(update=False, flevel=2)
    uwf.kernel(update=False, flevel=3)

    # Restricted workflow
    rwf = RUN(ratoms(), mode='restricted',log_name='RRUN.log')
    # FLO-SIC approximations
    rwf.kernel(update=False, flevel=0)
    rwf.kernel(update=False, flevel=1)
    rwf.kernel(update=False, flevel=2)
    rwf.kernel(update=False, flevel=3)


if __name__ == '__main__':
    test_run()

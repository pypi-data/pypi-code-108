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
from pyflosic2.sic.uflosic import UFLOSIC
from pyflosic2.sic.rflosic import RFLOSIC


def FLOSIC(mf, p):
    """
        PyFLOSIC2: FLO-SIC
        ------------------
        Use conditional inheritance to handle 
        different calculation modi. 

        Output
        ------
        mflo   : FLO-SIC object/instance of the correct mode
        p.mode : str(), 'unrestricted' or 'restricted'
    """
    if p.mode == 'unrestricted':
        return UFLOSIC(mf, p)
    if p.mode == 'restricted':
        return RFLOSIC(mf, p)


if __name__ == '__main__':
    from pyflosic2.test.knight_valley.flosic.test_flosic import test_flosic

    test_flosic()

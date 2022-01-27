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
from pyflosic2.test.knight_valley.uflo.test_uflo import test_uflo
from pyflosic2.test.knight_valley.rflo.test_rflo import test_rflo
from pyflosic2.test.knight_valley.flo.test_flo import test_flo
from pyflosic2.test.knight_valley.uflosic.test_uflosic import test_uflosic
from pyflosic2.test.knight_valley.rflosic.test_rflosic import test_rflosic
from pyflosic2.test.knight_valley.flosic.test_flosic import test_flosic
from pyflosic2.test.knight_valley.urun.test_urun import test_urun
from pyflosic2.test.knight_valley.rrun.test_rrun import test_rrun
from pyflosic2.test.knight_valley.run.test_run import test_run

def main():
    """
        main
        ----
        Main function to test PyFLOSIC2 functionalities

        Note
        ----
            - does not include workflow as there is not a unique FOD starting point 
            - testing calculations are performed with low numerics (low tier level and low flevel) 
            - thus results for full optimization may differ 
    """
    test_uflo()
    test_rflo()
    test_flo()
    test_uflosic()
    test_rflosic()
    test_flosic()
    test_urun()
    test_rrun() 
    test_run()

if __name__ == '__main__':
    main()

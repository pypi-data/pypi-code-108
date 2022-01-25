# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-24 16:05:07
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-24 16:06:49

import pytest

import pythermica
from pythermica.hdf5_process import h5dump

def test_h5dump():
    
    h5dump(pythermica.__path__[0] + "/../exemples/simulation_1/results_1/ionsat_deployed.temp.h5")
    
    

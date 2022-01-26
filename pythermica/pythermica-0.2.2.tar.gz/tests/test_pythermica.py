# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-21 13:21:38
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-25 09:41:05
#!/usr/bin/env python

"""Tests for `pythermica` package."""

import pytest

import pythermica
from pythermica import Thermica


def test_Thermica():
    """test Thermica Class with an example"""
    
    path = pythermica.__path__[0]+"/../exemples/simulation_1/results_1/"

    therm_results = Thermica(path, verbose=True)
    
    therm_results.dump_result_file_structure()
    
    sf_filenames = therm_results.get_filenames("solarflux")
    assert sf_filenames[0].name == "ionsat_deployed_3.0.sf.h5"
    
    pf_filenames = therm_results.get_filenames("earthflux")
    assert pf_filenames[0].name == "ionsat_deployed_3.0.pf.h5"

    temp_filenames = therm_results.get_filenames("temperature")
    assert temp_filenames[0].name == "ionsat_deployed.temp.h5"

    sf_filename = therm_results.get_solarflux_file()
    assert sf_filename.name == "ionsat_deployed_3.0.sf.h5"
    
    temp_filename = therm_results.get_temperature_file()
    assert temp_filename.name == "ionsat_deployed.temp.h5"
    
    value_sf, time_sf = therm_results.read_solarflux()
    
    assert len(time_sf) == 219
    assert len(value_sf) == 850
    
    value_temp = therm_results.get_temperature()
    assert value_temp.shape == (856, 1092)
    
    time_temp = therm_results.return_time_temperature()
    assert len(time_temp) == value_temp.shape[1]
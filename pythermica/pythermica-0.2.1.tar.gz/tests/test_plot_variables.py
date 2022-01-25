# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-24 16:07:45
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-24 16:59:59
import pytest
import shutil
import os, sys
import pythermica
from pythermica import Thermica
from pythermica.plot_variables import (plot_style,
                                       figure_over_nodes,
                                       totalInternalDissipation,
                                        )
                                        
from pathlib import Path

def test_plot_style():
    
    assert type(plot_style) == dict
    
def test_figure_over_nodes():
    
    path = pythermica.__path__[0]+"/../exemples/simulation_1/results_1/"

    therm_results = Thermica(path, verbose=False)

    time_temperature = therm_results.return_time_temperature()
    temperatures = therm_results.get_temperature()
    
    figure_over_nodes(therm_results = [therm_results],
                      temperatures=[temperatures],
                      times=[time_temperature],
                      n_orbits=8,
                      path_list=[path],
                      case_names=["Default"],
                      nodes_to_process=["/Powercard P60", "/Printed Circuits",
                                        "/Transponder (1)", "/Batteries"],
                      path_root="./",
                      name_yaxis="Temperature",
                      filename_prefix="")
    
    assert os.path.exists("./images")
    
    list_figures = list(Path("./images").glob("*.png"))
    
    assert len(list_figures) == 4
    
    shutil.rmtree('./images')

    
    
def test_plot_Internal_dissipation():
    path = pythermica.__path__[0]+"/../exemples/simulation_1/results_1/"

    therm_results = Thermica(path, verbose=False)
    time_temperature = therm_results.return_time_temperature()
    iq = therm_results.get_internal_dissipation()

    totalInternalDissipation( [therm_results],
                             [iq],
                             [time_temperature],
                             8,
                             [path],
                             ["default"],
                             )
    
    assert os.path.exists("./images")

    list_figures = list(Path("./images").glob("Total_IQ.png"))

    assert len(list_figures) == 1

    shutil.rmtree('./images')

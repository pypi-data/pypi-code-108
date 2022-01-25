import oftest, pytest
from os import path
import numpy as np
from itertools import islice

def test_read_csv_geoField():
    dir_name = path.dirname(path.abspath(__file__))
    filename = path.join(dir_name,"T.csv")
    df = oftest.read_csv_geoField(filename)
    patches_and_internal = set(df[4].unique().tolist())
    expected_Values = {'left', 'bottom', 'internal', 'top', 'right'}

    assert (len(patches_and_internal.difference(expected_Values)) == 0)

def test_log_status():
    dir_name = path.dirname(path.abspath(__file__))
    f_completed = path.join(dir_name,"log.completed")
    f_fe = path.join(dir_name,"log.fatalError")
    f_fpe = path.join(dir_name,"log.floatPointExp")
    f_running = path.join(dir_name,"log.running")

    assert oftest.case_status(f_completed) == "completed"
    assert oftest.case_status(f_fe) == "error"
    assert oftest.case_status(f_fpe) == "error"
    assert oftest.case_status(f_running) == "running"


def test_run_time():
    dir_name = path.dirname(path.abspath(__file__))
    f_completed = path.join(dir_name,"log.completed")
    t_exec, t_clock = oftest.run_time(f_completed)
    assert t_exec == 30.55
    assert t_clock == 30.0

def test_exp_results():
    test = oftest.expected_results([1,2],('isoAlpha',32))
    assert test['err_shape'] == 6.511E-02


# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
from bfit.gui.calculator_nmr_B1 import calculator_nmr_B1

def test_calculate_field():
    calc = calculator_nmr_B1(True)
    
    # voltage
    calc.volt.set('1')
    calc.entry_voltage.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.field.get()), 0.000960, 
                        err_msg = "calculator nmr B1 set volt = 1")
    calc.root.destroy()

def test_calculate_voltage():
    calc = calculator_nmr_B1(True)
    
    # field
    calc.field.set('1')
    calc.entry_field.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.volt.get()), 1042.171717, 
                        err_msg = "calculator nmr B1 set field = 1")
    calc.root.destroy()

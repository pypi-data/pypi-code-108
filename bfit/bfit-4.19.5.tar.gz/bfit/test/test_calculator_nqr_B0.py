# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
from bfit.gui.calculator_nqr_B0 import calculator_nqr_B0

def test_calculate_voltage():
    calc = calculator_nqr_B0(True)
    
    # voltage
    calc.current.set('1')
    calc.entry_current.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.field.get()), 2.3878, 
        err_msg = "calculator nqr B0 set current = 1, compared to online calculator")
    calc.root.destroy()
    
def test_calculate_field():
    calc = calculator_nqr_B0(True)
    
    # field
    calc.field.set('1')
    calc.entry_field.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.current.get()), 0.3729, 
                        err_msg = "calculator nqr B0 set field = 1, compared to online calculator")
    calc.root.destroy()

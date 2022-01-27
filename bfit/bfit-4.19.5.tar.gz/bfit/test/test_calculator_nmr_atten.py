# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
from bfit.gui.calculator_nmr_atten import calculator_nmr_atten

def test_calc_power():
    calc = calculator_nmr_atten(True)
    
    # power
    calc.power.set('100')
    calc.entry_power.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.dac.get()), 0, 
                        err_msg = "calculator nmr atten set power = 100%")
    
    calc.power.set('0')
    calc.entry_power.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.dac.get()), 2047, 
                        err_msg = "calculator nmr atten set power = 0%")
    calc.root.destroy()
    
def test_calc_dac():
    calc = calculator_nmr_atten(True)
    
    # dac
    calc.dac.set('0')
    calc.entry_dac.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.power.get()), 100, 
                        err_msg = "calculator nmr atten set dac = 0")
    
    calc.dac.set('2047')
    calc.entry_dac.focus_set()
    calc.calculate()
    assert_almost_equal(float(calc.power.get()), 0, 
                        err_msg = "calculator nmr atten set dac = 2047")
    calc.root.destroy()
    

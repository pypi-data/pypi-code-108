'''
Για να καλέσω τις συναρτήσεις γράφω στο UDF modules στο excel:
- streng.xwflib.xwf_main για να καλέσω τη συλολική
- streng.xwflib.(το όνομα του module) για να καλέσω μεμονωμένα
- ή κάνω ένα νέο .py αρχείο στον ίδο φάκελο με το αρχείο του excel και φωνάζω ότι θέλω εκεί
'''

# Γενικά imports
import pandas as pd
import xlwings as xw
import numpy as np

# xwf imports
from ..xwflib.math.xwf_math import *
from ..xwflib.codes.eurocodes.ec2_raw_ch3 import *
from ..xwflib.docs_examples import *
from ..xwflib.ppp.loads import *


from ..tools.bilin import Bilin



@xw.func
@xw.arg('x', np.array, ndim=1)
@xw.arg('y', np.array, ndim=1)
@xw.ret(index=False, expand='table')
def xwf_bilin(x, y, x_target):
    bl = Bilin(xtarget=x_target)
    bl.curve_ini.x = x
    bl.curve_ini.y = y
    bl.calc()

    _res = bl.bilinear_curve.all_quantities.to_panda_dataframe

    return _res


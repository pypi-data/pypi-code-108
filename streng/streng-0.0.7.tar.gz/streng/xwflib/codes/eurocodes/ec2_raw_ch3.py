import pandas as pd
import xlwings as xw
import numpy as np

from ....codes.eurocodes.ec2.raw.ch3.concrete import strength as conc_strength

@xw.func
def xwf_codes_eurocodes_ec2_ray_ch3_concrete_strength_fcm(fck):
    """fcm"""
    return conc_strength.fcm(fck)




# -*- coding: utf-8 -*-


"""
This module provide utils functions for the rest of the package

:author: C. Hottier
"""


import astropy.units as u 
from ccdproc import CCDData
from numpy import ndarray


def getlistccddata(inputlist, unit=u.adu):
    """process a list of fits filename or CCDData to obtain only CCDData

    :param inputlist: list or array-like of fits name or CCDData
    :param unit: the unit (astropy.units) to apply for reading CCDData, default adu
    :returns: list of CCDData

    """
    # res = []
    # for fits in inputlist:
    #     if isinstance(fits, CCDData):
    #         res += [fits]
    #     elif isinstance(fits, str):
    #         res += [CCDData.read(fits, unit=unit,)]

    # return res
    return [getccddata(f, unit=unit) for f in inputlist]

def getccddata(fits, unit=u.adu):
    """obtain a ccddata from inp 

    :param fits: input information filename, numpy.array, ccdata
    :param unit: the unit to use to create the CCDData, ignore if inp already CCDData, default adu
    :raise ValueError: if the type of fits is not suitable
    :returns: CCDData corresping to inp

    """
    if isinstance(fits, str) :
        return CCDData.read(fits, unit=unit)
    elif isinstance(fits, ndarray):
        return CCDData(fits, unit=unit)
    elif isinstance(fits, CCDData) :
        return fits
    else:
        raise ValueError("%s type can not be convert to CCData"%(type(fits)))

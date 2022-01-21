#!/usr/bin/env python

# ----------------------------------------------------------------------
# Author:        sebastian.piec@desy.de & yury.matveev@desy.de
# Last modified: 2017, December 12
# ----------------------------------------------------------------------

"""Auxiliary functions used in many different contexts.
"""

import datetime
import logging
import math
import os

import numpy as np


# ----------------------------------------------------------------------
def refresh_combo_box(comboBox, text):
    """Auxiliary function refreshing combo box with a given text.
    """
    idx = comboBox.findText(text)
    comboBox.blockSignals(True)
    if idx != -1:
        comboBox.setCurrentIndex(idx)
        comboBox.blockSignals(False)
        return True
    else:
        comboBox.setCurrentIndex(0)
        comboBox.blockSignals(False)
        return False


# ----------------------------------------------------------------------
def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

# ----------------------------------------------------------------------
def FWHM(data):
    """
    simple calculator of peak FWHM
    :param data:
    :return:
    """
    try:
        half_max = (np.amax(data) - np.amin(data)) / 2

        diff = np.sign(data - half_max)
        left_idx = np.where(diff > 0)[0][0]
        right_idx = np.where(diff > 0)[0][-1]
        return right_idx - left_idx  # return the difference (full width)
    except:
        return 0

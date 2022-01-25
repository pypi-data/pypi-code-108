# -*- coding: utf-8 -*-
# @Time     : 2021/12/1 17:00
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : registClass.py
# @Version  : Python 3.8.5 +

class EulerAngle(object):
    """
    Note: The format in the db is different from what we generated during the calculation
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = - z
        self.z = y


class Displacement(object):
    """
    Note: our format to 3js format
    """
    def __init__(self, x, y, z):
        self.x = x / 20
        self.y = z / 20
        self.z = y / 20

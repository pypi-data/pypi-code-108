# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-26 14:56:58
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-26 15:03:33

from pythermica.post_process import process_nwk_and_temperature
import pythermica

path = pythermica.__path__[0]+"/../exemples/model_test/"

process_nwk_and_temperature(path)

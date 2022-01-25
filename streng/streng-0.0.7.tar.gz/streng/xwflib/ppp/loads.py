import xlwings as xw
import numpy as np
import pandas as pd

from ...ppp.loads.slabs_to_beams import SlabLoadsToBeams


@xw.func
def xwf_ppp_loads_slabs_to_beams(lmax, lmin, slabtype, slabload, beam):
    sl = SlabLoadsToBeams(l_max = lmax,
                          l_min = lmin,
                          slab_type = slabtype,
                          slab_load = slabload)
    return sl.beams_loads[beam]



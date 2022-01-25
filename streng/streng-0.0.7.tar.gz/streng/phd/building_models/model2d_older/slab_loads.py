import xlwings as xw
from dataclasses import dataclass
from streng.xwflib.xwf_main import *
from streng.ppp.loads.slabs_to_beams import SlabLoadsToBeams


@dataclass
class slabs_phd:
    typos: str
    Lmax: float
    Lmin: float


# Πλαισιακοί φορείς
slabs_frames = {}
slabs_frames['Π1'] = slabs_phd(typos = '5a',
                              Lmax = 6.0, Lmin = 3.0)
slabs_frames['Π2'] = slabs_phd(typos = '6',
                              Lmax = 4.0, Lmin = 3.0)
slabs_frames['Π3'] = slabs_frames['Π1']                            


# Δίδυμοι φορείς 59 - 9ώροφα
slabs_duals9 = {}
slabs_duals9['Π1'] = slabs_phd(typos = '4',
                              Lmax = 6.0, Lmin = 3.0)
slabs_duals9['Π2'] = slabs_phd(typos = '5b',
                              Lmax = 6.0, Lmin = 3.0)
slabs_duals9['Π3'] = slabs_duals9['Π1']    

slabs_duals9['Π4'] = slabs_phd(typos = '5a',
                              Lmax = 6.0, Lmin = 3.0)
slabs_duals9['Π5'] = slabs_phd(typos = '6',
                              Lmax = 6.0, Lmin = 3.0)
slabs_duals9['Π6'] = slabs_duals9['Π4']   

slabs_duals9['Π7'] = slabs_duals9['Π4']
slabs_duals9['Π8'] = slabs_duals9['Π5']
slabs_duals9['Π9'] = slabs_duals9['Π7']


# Δίδυμοι φορείς 59 - 4ώροφα
slabs_duals4 = {}
slabs_duals4['Π1'] = slabs_phd(typos = '4',
                              Lmax = 4.5, Lmin = 4.0)
slabs_duals4['Π2'] = slabs_phd(typos = '5b',
                              Lmax = 4.5, Lmin = 4.0)
slabs_duals4['Π3'] = slabs_duals4['Π1']                                

slabs_duals4['Π4'] = slabs_phd(typos = '5a',
                              Lmax = 4.5, Lmin = 4.0)
slabs_duals4['Π5'] = slabs_phd(typos = '6',
                              Lmax = 4.5, Lmin = 4.0)
slabs_duals4['Π6'] = slabs_duals4['Π4'] 

slabs_duals4['Π7'] = slabs_duals4['Π4']
slabs_duals4['Π8'] = slabs_duals4['Π5']
slabs_duals4['Π9'] = slabs_duals4['Π7']


@xw.func
def phd_beam_loads_from_slabs(building_type, slab_beam_combo, slab_load):
    _beam_load = 0

    if slab_beam_combo != '':
        # print(slab_beam_combo + str(type(slab_beam_combo)))

        slab_beams = slab_beam_combo.split(',')

        for slab_beam in slab_beams:
            sl_b = slab_beam.split(':')
            sl_name, sl_beam_checked = sl_b[0], int(sl_b[1])
            if building_type == 'frames':
                sl = slabs_frames[sl_name]
            elif building_type == 'duals4':
                sl = slabs_duals4[sl_name]
            elif building_type == 'duals9':
                sl = slabs_duals9[sl_name]
            else:
                sl=None

            sltb = SlabLoadsToBeams(l_max = sl.Lmax,
                                    l_min = sl.Lmin,
                                    slab_type = sl.typos,
                                    slab_load = slab_load)
            _beam_load += sltb.beams_loads[sl_beam_checked]
    return _beam_load



   



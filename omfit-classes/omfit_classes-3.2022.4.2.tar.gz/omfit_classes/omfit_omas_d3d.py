"""
Functions for adding DIII-D hardware description data to the IMAS schema by writing data to ODS instances
"""

try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

import numpy as np
import copy
from omfit_classes.omfit_mds import OMFITmds, OMFITmdsValue
from omfit_classes.utils_base import compare_version

try:
    import omas

    imas_version = omas.ODS().imas_version
except Exception:
    imas_version = '0.0'

__all__ = []


# Decorators
def _id(obj):
    """Trivial decorator as an alternative to make_available()"""
    return obj


def make_available(f):
    """Decorator for listing a function in __all__ so it will be readily available in other scripts"""
    __all__.append(f.__name__)
    return f


def make_available_if(condition):
    """
    Make available only if a condition is met

    :param condition: bool
        True: make_available decorator is used and function is added to __all__ to be readily available
        False: _id decorator is used, function is not added to __all__, and it cannot be accessed quite so easily
            Some functions inspect __all__ to determine which hardware systems are available
    """
    if condition:
        return make_available
    return _id


# Utilities
def printq(*args):
    return printd(*args, topic='omfit_omas_d3d')


# Hardware descriptor functions
@make_available
def setup_gas_injection_hardware_description_d3d(ods, shot):
    """
    Sets up DIII-D gas injector data.

    R and Z are from the tips of the arrows in puff_loc.pro; phi from angle listed in labels in puff_loc.pro .
    I recorded the directions of the arrows on the EFITviewer overlay, but I don't know how to include them in IMAS, so
    I commented them out.

    Warning: changes to gas injector configuration with time are not yet included. This is just the best picture I could
    make of the 2018 configuration.

    Data sources:
    EFITVIEWER: iris:/fusion/usc/src/idl/efitview/diagnoses/DIII-D/puff_loc.pro accessed 2018 June 05, revised 20090317
    DIII-D webpage: https://diii-d.gat.com/diii-d/Gas_Schematic accessed 2018 June 05
    DIII-D wegpage: https://diii-d.gat.com/diii-d/Gas_PuffLocations accessed 2018 June 05

    Updated 2018 June 05 by David Eldon

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    if shot < 100775:
        warnings.warn('DIII-D Gas valve locations not applicable for shots earlier than 100775 (2000 JAN 17)')

    imas_version = getattr(ods, 'imas_version', None)
    separate_valves = imas_version is not None and compare_version(imas_version, "3.34.0") >= 0

    i = 0  # Pipe index
    iv = 0  # Valve index

    def pipe_copy(pipe_in):
        pipe_out = ods['gas_injection']['pipe'][i]
        for field in ['name', 'exit_position.r', 'exit_position.z', 'exit_position.phi']:
            pipe_out[field] = copy.copy(pipe_in[field])
        if separate_valves:
            valve_out = ods['gas_injection']['valve'][iv]
            pipe_out['valve_indices'] = [iv]
        else:
            valve_out = None
        return pipe_out, valve_out

    # PFX1
    pipe_indices = []
    for angle in [12, 139, 259]:  # degrees, DIII-D hardware left handed coords
        pipe_pfx1 = ods['gas_injection']['pipe'][i]
        pipe_pfx1['name'] = 'PFX1_{:03d}'.format(angle)
        pipe_pfx1['exit_position']['r'] = 1.286  # m
        pipe_pfx1['exit_position']['z'] = 1.279  # m
        pipe_pfx1['exit_position']['phi'] = -np.pi / 180.0 * angle  # radians, right handed
        if separate_valves:
            pipe_pfx1['valve_indices'] = [iv]
        else:
            pipe_pfx1['valve'][0]['identifier'] = 'PFX1'
        pipe_indices += [i]

        dr = -1.116 + 1.286
        dz = -1.38 + 1.279
        # pipea['exit_position']['direction'] = 180/np.pi * tan(dz/dr) if dr != 0 else 90 * sign(dz)
        pipe_pfx1['second_point']['phi'] = pipe_pfx1['exit_position']['phi']
        pipe_pfx1['second_point']['r'] = pipe_pfx1['exit_position']['r'] + dr
        pipe_pfx1['second_point']['z'] = pipe_pfx1['exit_position']['z'] + dz
        i += 1
    if separate_valves:
        valve_pfx1 = ods['gas_injection']['valve'][iv]
        valve_pfx1['identifier'] = 'PFX1'
        valve_pfx1['name'] = 'PFX1'
        valve_pfx1['pipe_indices'] = pipe_indices
    iv += 1

    # PFX2 injects at the same poloidal locations as PFX1, but at different toroidal angles
    pipe_indices = []
    for angle in [79, 199, 319]:  # degrees, DIII-D hardware left handed coords
        pipe_copy(pipe_pfx1)
        pipe_pfx2 = ods['gas_injection']['pipe'][i]
        pipe_pfx2['name'] = 'PFX2_{:03d}'.format(angle)
        pipe_pfx2['exit_position']['phi'] = -np.pi / 180.0 * angle  # rad
        if separate_valves:
            pipe_pfx2['valve_indices'] = [iv]
        else:
            pipe_pfx2['valve'][0]['identifier'] = 'PFX2'
        pipe_indices += [i]
        pipe_pfx2['second_point']['phi'] = pipe_pfx2['exit_position']['phi']
        i += 1
    if separate_valves:
        valve_pfx2 = ods['gas_injection']['valve'][iv]
        valve_pfx2['identifier'] = 'PFX2'
        valve_pfx2['name'] = 'PFX2'
        valve_pfx2['pipe_indices'] = pipe_indices
    iv += 1

    # GAS A
    pipea = ods['gas_injection']['pipe'][i]
    pipea['name'] = 'GASA_300'
    pipea['exit_position']['r'] = 1.941  # m
    pipea['exit_position']['z'] = 1.01  # m
    pipea['exit_position']['phi'] = -np.pi / 180.0 * 300  # rad
    # pipea['exit_position']['direction'] = 270.  # degrees, giving dir of pipe leading towards injector, up is 90
    pipea['second_point']['phi'] = pipea['exit_position']['phi']
    pipea['second_point']['r'] = pipea['exit_position']['r']
    pipea['second_point']['z'] = pipea['exit_position']['z'] - 0.01
    if separate_valves:
        pipea['valve_indices'] = [iv]
        valvea = ods['gas_injection']['valve'][iv]
        valvea['identifier'] = 'GASA'
        valvea['name'] = 'GASA'
        valvea['pipe_indices'] = [i]
    else:
        pipea['valve'][0]['identifier'] = 'GASA'
    i += 1
    iv += 1

    # GAS B injects in the same place as GAS A
    pipeb, valveb = pipe_copy(pipea)
    pipeb['name'] = 'GASB_300'
    if separate_valves:
        valveb['name'] = valveb['identifier'] = 'GASB'
        valveb['pipe_indices'] = [i]
    else:
        pipeb['valve'][0]['identifier'] = 'GASB'
    i += 1
    iv += 1

    # GAS C
    pipec = ods['gas_injection']['pipe'][i]
    pipec['name'] = 'GASC_000'
    pipec['exit_position']['r'] = 1.481  # m
    pipec['exit_position']['z'] = -1.33  # m
    pipec['exit_position']['phi'] = -np.pi / 180.0 * 0
    # pipec['exit_position']['direction'] = 90.  # degrees, giving direction of pipe leading towards injector
    pipec['second_point']['phi'] = pipec['exit_position']['phi']
    pipec['second_point']['r'] = pipec['exit_position']['r']
    pipec['second_point']['z'] = pipec['exit_position']['z'] + 0.01
    if separate_valves:
        valvec = ods['gas_injection']['valve'][iv]
        valvec['name'] = 'GASC'
        valvec['identifier'] = 'GASC'
        valvec['pipe_indices'] = [i]
        pipec['valve_indices'] = [iv]
    else:
        pipec['valve'][0]['identifier'] = 'GASC'

    i += 1
    iv += 1

    # GAS D injects at the same poloidal location as GAS A, but at a different toroidal angle.
    # There is a GASD piezo valve that splits into four injectors, all of which have their own gate valves and can be
    # turned on/off independently. Normally, only one would be used at at a time.
    pipe_copy(pipea)
    piped = ods['gas_injection']['pipe'][i]
    piped['name'] = 'GASD_225'  # This is the injector name
    piped['exit_position']['phi'] = -np.pi / 180.0 * 225
    piped['second_point']['phi'] = piped['exit_position']['phi']
    if separate_valves:
        valved = ods['gas_injection']['valve'][iv]
        valved['name'] = valved['identifier'] = 'GASD'  # This is the piezo name
        valved['pipe_indices'] = [i]
        piped['valve_indices'] = [iv]
    else:
        piped['valve'][0]['identifier'] = 'GASD'
    i += 1
    iv += 1

    # GASE is at the same poloidal location as GASC
    pipee, valvee = pipe_copy(pipec)
    if separate_valves:
        valvee['name'] = valvee['identifier'] = 'GASE'
        valvee['pipe_indices'] = [i]
    else:
        pipee['valve'][0]['identifier'] = 'GASE'
    i += 1
    iv += 1

    # Spare 225 is an extra branch of the GASD line after the GASD piezo (might not have a valve)
    pipe_copy(piped)
    pipes225 = ods['gas_injection']['pipe'][i]
    pipes225['name'] = 'Spare_225'  # This is the injector name
    i += 1

    # RF_170 and RF_190: gas ports near the 180 degree antenna, on the GASD line
    # I don't think these are connected anymore, but I don't know the shot number after which they were removed.
    for angle in [170, 190]:
        pipe_rf = ods['gas_injection']['pipe'][i]
        pipe_rf['name'] = 'RF_{:03d}'.format(angle)
        pipe_rf['exit_position']['r'] = 2.38  # m
        pipe_rf['exit_position']['z'] = -0.13  # m
        pipe_rf['exit_position']['phi'] = -np.pi / 180.0 * angle  # rad
        i += 1

    # DRDP
    pipe_copy(piped)
    pipedrdp = ods['gas_injection']['pipe'][i]
    pipedrdp['name'] = 'DRDP_225'
    if separate_valves:
        pipedrdp['valve_indices'] = [iv]
        valvedrdp = ods['gas_injection']['valve'][iv]
        valvedrdp['identifier'] = 'DRDP'
        valvedrdp['name'] = 'DRDP'
        valvedrdp['pipe_indices'] = [i]
    else:
        pipedrdp['valve'][0]['identifier'] = 'DRDP'
    i += 1
    iv += 1

    # UOB
    pipe_indices = []
    for angle in [45, 165, 285]:
        pipe_uob = ods['gas_injection']['pipe'][i]
        pipe_uob['name'] = 'UOB_{:03d}'.format(angle)
        pipe_uob['exit_position']['r'] = 1.517  # m
        pipe_uob['exit_position']['z'] = 1.267  # m
        pipe_uob['exit_position']['phi'] = -np.pi / 180.0 * angle
        pipe_indices += [i]
        if separate_valves:
            pipe_uob['valve_indices'] = [iv]
        else:
            pipe_uob['valve'][0]['identifier'] = 'UOB'
        # pipe_uob['exit_position']['direction'] = 270.  # degrees, giving dir of pipe leading to injector, up is 90
        i += 1
    if separate_valves:
        valve_uob = ods['gas_injection']['valve'][iv]
        valve_uob['name'] = valve_uob['identifier'] = 'UOB'
        valve_uob['pipe_indices'] = pipe_indices
    iv += 1

    # LOB1
    pipe_indices = []
    for angle in [30, 120]:
        pipe_lob1 = ods['gas_injection']['pipe'][i]
        pipe_lob1['name'] = 'LOB1_{:03d}'.format(angle)
        pipe_lob1['exit_position']['r'] = 1.941  # m
        pipe_lob1['exit_position']['z'] = -1.202  # m
        pipe_lob1['exit_position']['phi'] = -np.pi / 180.0 * angle
        if separate_valves:
            pipe_lob1['valve_indices'] = [iv]
        else:
            pipe_lob1['valve'][0]['identifier'] = 'LOB1'
        pipe_indices += [i]
        # pipe_lob1['exit_position']['direction'] = 180.  # degrees, giving dir of pipe leading to injector; up is 90
        i += 1
    if separate_valves:
        valve_lob1 = ods['gas_injection']['valve'][iv]
        valve_lob1['name'] = valve_lob1['identifier'] = 'LOB1'
        valve_lob1['pipe_indices'] = pipe_indices
    iv += 1

    # Spare 75 is an extra branch of the GASC line after the LOB1 piezo
    pipes75 = ods['gas_injection']['pipe'][i]
    pipes75['name'] = 'Spare_075'
    pipes75['exit_position']['r'] = 2.249  # m (approximate / estimated from still image)
    pipes75['exit_position']['z'] = -0.797  # m (approximate / estimated from still image)
    pipes75['exit_position']['phi'] = 75  # degrees, DIII-D hardware left handed coords
    if separate_valves:
        pipes75['valve_indices'] = pipe_lob1['valve_indices']
        valve_lob1['pipe_indices'] = np.append(valve_lob1['pipe_indices'], [i])
    else:
        pipes75['valve'][0]['identifier'] = 'LOB1'
    # pipes75['exit_position']['direction'] = 180.  # degrees, giving direction of pipe leading towards injector
    i += 1

    # RF_010 & 350
    for angle in [10, 350]:
        pipe_rf_lob1 = ods['gas_injection']['pipe'][i]
        pipe_rf_lob1['name'] = 'RF_{:03d}'.format(angle)
        pipe_rf_lob1['exit_position']['r'] = 2.38  # m
        pipe_rf_lob1['exit_position']['z'] = -0.13  # m
        pipe_rf_lob1['exit_position']['phi'] = -np.pi / 180.0 * angle
        if separate_valves:
            pipe_rf_lob1['valve_indices'] = pipe_lob1['valve_indices']
            valve_lob1['pipe_indices'] = np.append(valve_lob1['pipe_indices'], [i])
        else:
            pipe_rf_lob1['valve'][0]['identifier'] = 'LOB1'
        # pipe_rf10['exit_position']['direction'] = 180.  # degrees, giving dir of pipe leading to injector; up is 90
        i += 1

    # DiMES chimney
    pipe_dimesc = ods['gas_injection']['pipe'][i]
    pipe_dimesc['name'] = 'DiMES_Chimney_165'
    pipe_dimesc['exit_position']['r'] = 1.481  # m
    pipe_dimesc['exit_position']['z'] = -1.33  # m
    pipe_dimesc['exit_position']['phi'] = -np.pi / 180.0 * 165
    if separate_valves:
        pipe_dimesc['valve_indices'] = [iv]
        cpgas_valve = ods['gas_injection']['valve'][iv]
        cpgas_valve['identifier'] = '240R-2'
        cpgas_valve['name'] = '240R-2 (PCS use GASD)'
        cpgas_valve['pipe_indices'] = [i]
    else:
        pipe_dimesc['valve'][0]['identifier'] = '240R-2'
    # pipe_dimesc['exit_position']['direction'] = 90.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1
    iv += 1

    # CPBOT
    pipe_cpbot = ods['gas_injection']['pipe'][i]
    pipe_cpbot['name'] = 'CPBOT_150'
    pipe_cpbot['exit_position']['r'] = 1.11  # m
    pipe_cpbot['exit_position']['z'] = -1.33  # m
    pipe_cpbot['exit_position']['phi'] = -np.pi / 180.0 * 150
    if separate_valves:
        pipe_cpbot['valve_indices'] = pipe_dimesc['valve_indices']
        cpgas_valve['pipe_indices'] = np.append(cpgas_valve['pipe_indices'], [i])
    else:
        pipe_cpbot['valve'][0]['identifier'] = '240R-2'
    # pipe_cpbot['exit_position']['direction'] = 0.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1

    # LOB2 injects at the same poloidal locations as LOB1, but at different toroidal angles
    if separate_valves:
        valve_lob2 = ods['gas_injection']['valve'][iv]
        valve_lob2['identifier'] = 'LOB2'
        valve_lob2['name'] = 'LOB2'
        valve_lob2['pipe_indices'] = []
    for angle in [210, 300]:
        pipe_copy(pipe_lob1)
        pipe_lob2 = ods['gas_injection']['pipe'][i]
        pipe_lob2['name'] = 'LOB2_{:03d}'.format(angle)
        pipe_lob2['exit_position']['phi'] = -np.pi / 180.0 * angle  # degrees, DIII-D hardware left handed coords
        if separate_valves:
            pipe_lob2['valve_indices'] = [iv]
            valve_lob2['pipe_indices'] = np.append(valve_lob2['pipe_indices'], [i])
        else:
            pipe_lob2['valve'][0]['identifier'] = 'LOB2'
        i += 1
    iv += 1

    # Dimes floor tile 165
    pipe_copy(pipec)
    pipe_dimesf = ods['gas_injection']['pipe'][i]
    pipe_dimesf['name'] = 'DiMES_Tile_160'
    pipe_dimesf['exit_position']['phi'] = -np.pi / 180.0 * 165
    if separate_valves:
        pipe_dimesf['valve_indices'] = pipe_lob2['valve_indices']
        valve_lob2['pipe_indices'] = np.append(valve_lob2['pipe_indices'], [i])
    else:
        pipe_dimesf['valve'][0]['identifier'] = 'LOB2'
    i += 1

    # RF COMB
    pipe_rfcomb = ods['gas_injection']['pipe'][i]
    pipe_rfcomb['name'] = 'RF_COMB_'
    pipe_rfcomb['exit_position']['r'] = 2.38  # m
    pipe_rfcomb['exit_position']['z'] = -0.13  # m
    # pipe_rfcomb['exit_position']['phi'] = Unknown, sorry
    if separate_valves:
        pipe_rfcomb['valve_indices'] = pipe_lob2['valve_indices']
        valve_lob2['pipe_indices'] = np.append(valve_lob2['pipe_indices'], [i])
    else:
        pipe_rfcomb['valve'][0]['identifier'] = 'LOB2'
    # pipe_rf307['exit_position']['direction'] = 180.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1

    # RF307
    pipe_rf307 = ods['gas_injection']['pipe'][i]
    pipe_rf307['name'] = 'RF_307'
    pipe_rf307['exit_position']['r'] = 2.38  # m
    pipe_rf307['exit_position']['z'] = -0.13  # m
    pipe_rf307['exit_position']['phi'] = -np.pi / 180.0 * 307
    if separate_valves:
        pipe_rf307['valve_indices'] = pipe_lob2['valve_indices']
        valve_lob2['pipe_indices'] = np.append(valve_lob2['pipe_indices'], [i])
    else:
        pipe_rf307['valve'][0]['identifier'] = 'LOB2'
    # pipe_rf307['exit_position']['direction'] = 180.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1

    # GAS H injects in the same place as GAS C
    pipe_copy(pipec)
    pipeh = ods['gas_injection']['pipe'][i]
    pipeh['name'] = 'GASH_000'
    if separate_valves:
        pipeh['valve_indices'] = []  # This one's not on the manifold schematic
    i += 1

    # GAS I injects in the same place as GAS C
    pipe_copy(pipec)
    pipei = ods['gas_injection']['pipe'][i]
    pipei['name'] = 'GASI_000'
    if separate_valves:
        pipei['valve_indices'] = []  # This one's not on the manifold schematic
    i += 1

    # GAS J injects in the same place as GAS D
    pipe_copy(piped)
    pipej = ods['gas_injection']['pipe'][i]
    pipej['name'] = 'GASJ_225'
    if separate_valves:
        pipej['valve_indices'] = []  # This one's not on the manifold schematic
    i += 1

    # RF260
    pipe_rf260 = ods['gas_injection']['pipe'][i]
    pipe_rf260['name'] = 'RF_260'
    pipe_rf260['exit_position']['r'] = 2.38  # m
    pipe_rf260['exit_position']['z'] = 0.14  # m
    pipe_rf260['exit_position']['phi'] = -np.pi / 180.0 * 260
    if separate_valves:
        pipe_rf260['valve_indices'] = pipe_lob2['valve_indices']  # Seems to have been removed. May have been on LOB2, though.
        valve_lob2['pipe_indices'] = np.append(valve_lob2['pipe_indices'], [i])
    else:
        pipe_rf260['valve'][0]['identifier'] = 'LOB2'
    # pipe_rf260['exit_position']['direction'] = 180.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1

    # CPMID
    pipe_cpmid = ods['gas_injection']['pipe'][i]
    pipe_cpmid['name'] = 'CPMID'
    pipe_cpmid['exit_position']['r'] = 0.9  # m
    pipe_cpmid['exit_position']['z'] = -0.2  # m
    if separate_valves:
        pipe_cpmid['valve_indices'] = []  # Seems to have been removed. Not on schematic.
    # pipe_cpmid['exit_position']['direction'] = 0.  # degrees, giving dir of pipe leading towards injector, up is 90
    i += 1

    return {}


# The magnetic hardware description function (for bpol probes and flux loops) has been generalized & is in omfit_omas.py

# The pulse_schedule hardware description function has been generalized and is in omfit_omas.py

# The position_control hardware description function (a subset of pulse_schedule) is in omfit_omas.py


@make_available
def setup_pf_active_hardware_description_d3d(ods, *args):
    r"""
    Adds DIII-D tokamak poloidal field coil hardware geometry to ODS
    :param ods: ODS instance

    :param \*args: catch unused args to allow a consistent call signature for hardware description functions

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    from omfit_classes.omfit_omas_utils import pf_coils_to_ods

    # From  iris:/fusion/usc/src/idl/efitview/diagnoses/DIII-D/coils.dat , accessed 2018 June 08  D. Eldon
    fc_dat = np.array(
        [  # R        Z       dR      dZ    tilt1  tilt2
            [0.8608, 0.16830, 0.0508, 0.32106, 0.0, 0.0],  # 0 in the last column really means 90 degrees.
            [0.8614, 0.50810, 0.0508, 0.32106, 0.0, 0.0],
            [0.8628, 0.84910, 0.0508, 0.32106, 0.0, 0.0],
            [0.8611, 1.1899, 0.0508, 0.32106, 0.0, 0.0],
            [1.0041, 1.5169, 0.13920, 0.11940, 45.0, 0.0],
            [2.6124, 0.4376, 0.17320, 0.1946, 0.0, 92.40],
            [2.3733, 1.1171, 0.1880, 0.16920, 0.0, 108.06],
            [1.2518, 1.6019, 0.23490, 0.08510, 0.0, 0.0],
            [1.6890, 1.5874, 0.16940, 0.13310, 0.0, 0.0],
            [0.8608, -0.17370, 0.0508, 0.32106, 0.0, 0.0],
            [0.8607, -0.51350, 0.0508, 0.32106, 0.0, 0.0],
            [0.8611, -0.85430, 0.0508, 0.32106, 0.0, 0.0],
            [0.8630, -1.1957, 0.0508, 0.32106, 0.0, 0.0],
            [1.0025, -1.5169, 0.13920, 0.11940, -45.0, 0.0],
            [2.6124, -0.4376, 0.17320, 0.1946, 0.0, -92.40],
            [2.3834, -1.1171, 0.1880, 0.16920, 0.0, -108.06],
            [1.2524, -1.6027, 0.23490, 0.08510, 0.0, 0.0],
            [1.6889, -1.5780, 0.16940, 0.13310, 0.0, 0.0],
        ]
    )

    ods = pf_coils_to_ods(ods, fc_dat)

    for i in range(len(fc_dat[:, 0])):
        fcid = 'F{}{}'.format((i % 9) + 1, 'AB'[int(fc_dat[i, 1] < 0)])
        ods['pf_active.coil'][i]['name'] = ods['pf_active.coil'][i]['identifier'] = fcid
        ods['pf_active.coil'][i]['element.0.identifier'] = fcid

    return {}


@make_available
def setup_interferometer_hardware_description_d3d(ods, shot):
    """
    Writes DIII-D CO2 interferometer chord locations into ODS.

    The chord endpoints ARE NOT RIGHT. Only the R for vertical lines or Z for horizontal lines is right.

    Data sources:
    DIII-D webpage: https://diii-d.gat.com/diii-d/Mci accessed 2018 June 07  D. Eldon

    :param ods: an OMAS ODS instance

    :param shot: int

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """

    # As of 2018 June 07, DIII-D has four interferometers
    # phi angles are compliant with odd COCOS
    ods['interferometer.channel.0.identifier'] = 'r0'
    r0 = ods['interferometer.channel.0.line_of_sight']
    r0['first_point.phi'] = r0['second_point.phi'] = 225 * (-np.pi / 180.0)
    r0['first_point.r'], r0['second_point.r'] = 3.0, 0.8  # These are not the real endpoints
    r0['first_point.z'] = r0['second_point.z'] = 0.0

    for i, r in enumerate([1.48, 1.94, 2.10]):
        ods['interferometer.channel'][i + 1]['identifier'] = 'v{}'.format(i + 1)
        los = ods['interferometer.channel'][i + 1]['line_of_sight']
        los['first_point.phi'] = los['second_point.phi'] = 240 * (-np.pi / 180.0)
        los['first_point.r'] = los['second_point.r'] = r
        los['first_point.z'], los['second_point.z'] = -1.8, 1.8  # These are not the real points

    for i in range(len(ods['interferometer.channel'])):
        ch = ods['interferometer.channel'][i]
        ch['line_of_sight.third_point'] = copy.copy(ch['line_of_sight.first_point'])

    if shot < 125406:
        printw(
            'DIII-D CO2 pointnames were different before shot 125406. The physical locations of the chords seems to '
            'have been the same, though, so there has not been a problem yet (I think).'
        )

    return {}


def find_thomson_lens_d3d(shot, hw_call_sys, hw_revision='blessed'):
    """Read the Thomson scattering hardware map to figure out which lens each chord looks through"""
    cal_call = '.ts.{}.header.calib_nums'.format(hw_revision)
    cal_set = OMFITmdsValue(server='DIII-D', treename='ELECTRONS', shot=shot, TDI=cal_call).data()[0]
    hwi_call = '.{}.hwmapints'.format(hw_call_sys)
    printq('  Reading hw map int values: treename = "tscal", cal_set = {}, hwi_call = {}'.format(cal_set, hwi_call))
    try:
        hw_ints = OMFITmdsValue(server='DIII-D', treename='tscal', shot=cal_set, TDI=hwi_call).data()
    except MDSplus.MdsException:
        printw('WARNING: Error reading Thomson scattering hardware map to determine which lenses were used!')
        return None
    else:
        if len(np.shape(hw_ints)) < 2:
            # Contingency needed for cases where all view-chords are taken off of divertor laser and reassigned to core
            hw_ints = hw_ints.reshape(1, -1)
        hw_lens = hw_ints[:, 2]
        return hw_lens


@make_available
def setup_thomson_scattering_hardware_description_d3d(ods, shot, revision='BLESSED'):
    """
    Gathers DIII-D Thomson measurement locations from MDSplus and loads them into OMAS

    :param revision: string
        Thomson scattering data revision, like 'BLESSED', 'REVISIONS.REVISION00', etc.

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    printq('Setting up DIII-D Thomson locations...')

    tsdat = OMFITmds(server='DIII-D', treename='ELECTRONS', shot=shot)['TS'][revision]

    is_subsys = np.array([np.all([item in tsdat[k] for item in ['DENSITY', 'TEMP', 'R', 'Z']]) for k in list(tsdat.keys())])
    subsystems = np.array(list(tsdat.keys()))[is_subsys]

    i = 0
    for sub in subsystems:
        lenses = find_thomson_lens_d3d(shot, sub, revision)
        try:
            nc = len(tsdat[sub]['R'].data())
        except (TypeError, KeyError):
            nc = 0
        for j in range(nc):
            ch = ods['thomson_scattering']['channel'][i]
            ch['name'] = 'TS_{sub:}_r{lens:+0d}_{ch:}'.format(sub=sub.lower(), ch=j, lens=lenses[j] if lenses is not None else -9)
            ch['identifier'] = '{}{:02d}'.format(sub[0], j)
            for pos in ['R', 'Z', 'PHI']:
                ch['position'][pos.lower()] = tsdat[sub][pos].data()[j] * (-np.pi / 180.0 if pos == 'PHI' else 1)
            i += 1
    return {}


@make_available
def setup_charge_exchange_hardware_description_d3d(ods, shot, analysis_type='CERQUICK'):
    """
    Gathers DIII-D CER measurement locations from MDSplus and loads them into OMAS

    :param analysis_type: string
        CER analysis quality level like CERQUICK, CERAUTO, or CERFIT.  CERQUICK is probably fine.

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    printq('Setting up DIII-D CER locations...')

    cerdat = OMFITmds(server='DIII-D', treename='IONS', shot=shot)['CER'][analysis_type]

    subsystems = np.array([k for k in list(cerdat.keys()) if 'CHANNEL01' in list(cerdat[k].keys())])

    i = 0
    for sub in subsystems:
        try:
            channels = [k for k in list(cerdat[sub].keys()) if 'CHANNEL' in k]
        except (TypeError, KeyError):
            channels = []
        for j, channel in enumerate(channels):
            inc = 0
            for pos in ['R', 'Z', 'VIEW_PHI']:
                postime = cerdat[sub][channel]['TIME'].data()
                posdat = cerdat[sub][channel][pos].data()
                if postime is not None:
                    inc = 1
                    ch = ods['charge_exchange']['channel'][i]
                    ch['name'] = 'imCERtang_{sub:}{ch:02d}'.format(sub=sub.lower()[0], ch=j + 1)
                    ch['identifier'] = '{}{:02d}'.format(sub[0], j + 1)
                    chpos = ch['position'][pos.lower().split('_')[-1]]
                    chpos['time'] = postime / 1000.0  # Convert ms to s
                    chpos['data'] = posdat * -np.pi / 180.0 if (pos == 'VIEW_PHI') and posdat is not None else posdat
            i += inc
    return {}


@make_available
def setup_bolometer_hardware_description_d3d(ods, shot):
    """
    Load DIII-D bolometer chord locations into the ODS

    Data sources:
    - iris:/fusion/usc/src/idl/efitview/diagnoses/DIII-D/bolometerpaths.pro
    - OMFIT-source/modules/_PCS_prad_control/SETTINGS/PHYSICS/reference/DIII-D/bolometer_geo , access 2018June11 Eldon

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    printq('Setting up DIII-D bolometer locations...')

    if shot < 91000:
        xangle = (
            np.array(
                [
                    292.40,
                    288.35,
                    284.30,
                    280.25,
                    276.20,
                    272.15,
                    268.10,
                    264.87,
                    262.27,
                    259.67,
                    257.07,
                    254.47,
                    251.87,
                    249.27,
                    246.67,
                    243.81,
                    235.81,
                    227.81,
                    219.81,
                    211.81,
                    203.81,
                    195.81,
                    187.81,
                    179.80,
                    211.91,
                    206.41,
                    200.91,
                    195.41,
                    189.91,
                    184.41,
                    178.91,
                    173.41,
                    167.91,
                    162.41,
                    156.91,
                    156.30,
                    149.58,
                    142.86,
                    136.14,
                    129.77,
                    126.77,
                    123.77,
                    120.77,
                    117.77,
                    114.77,
                    111.77,
                    108.77,
                    102.25,
                ]
            )
            * np.pi
            / 180.0
        )  # Converted to rad

        xangle_width = None

        zxray = (
            np.array(
                [
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    124.968,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    129.870,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -81.153,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                    -72.009,
                ]
            )
            / 100.0
        )  # Converted to m

        rxray = (
            np.array(
                [
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    196.771,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    190.071,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    230.720,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                    232.900,
                ]
            )
            / 100.0
        )  # Converted to m

    else:
        xangle = (
            np.array(
                [  # There is a bigger step before the very last channel. Found in two different sources.
                    269.4,
                    265.6,
                    261.9,
                    258.1,
                    254.4,
                    250.9,
                    247.9,
                    244.9,
                    241.9,
                    238.9,
                    235.9,
                    232.9,
                    228.0,
                    221.3,
                    214.5,
                    208.2,
                    201.1,
                    194.0,
                    187.7,
                    182.2,
                    176.7,
                    171.2,
                    165.7,
                    160.2,
                    213.7,
                    210.2,
                    206.7,
                    203.2,
                    199.7,
                    194.4,
                    187.4,
                    180.4,
                    173.4,
                    166.4,
                    159.4,
                    156.0,
                    149.2,
                    142.4,
                    135.8,
                    129.6,
                    126.6,
                    123.6,
                    120.6,
                    117.6,
                    114.6,
                    111.6,
                    108.6,
                    101.9,
                ]
            )
            * np.pi
            / 180.0
        )  # Converted to rad

        xangle_width = (
            np.array(
                [
                    3.082,
                    3.206,
                    3.317,
                    3.414,
                    3.495,
                    2.866,
                    2.901,
                    2.928,
                    2.947,
                    2.957,
                    2.960,
                    2.955,
                    6.497,
                    6.342,
                    6.103,
                    6.331,
                    6.697,
                    6.979,
                    5.510,
                    5.553,
                    5.546,
                    5.488,
                    5.380,
                    5.223,
                    3.281,
                    3.348,
                    3.402,
                    3.444,
                    3.473,
                    6.950,
                    6.911,
                    6.768,
                    6.526,
                    6.188,
                    5.757,
                    5.596,
                    5.978,
                    6.276,
                    6.490,
                    2.979,
                    2.993,
                    2.998,
                    2.995,
                    2.984,
                    2.965,
                    2.938,
                    2.902,
                    6.183,
                ]
            )
            * np.pi
            / 180.0
        )  # Angular full width of the view-chord: calculations assume it's a symmetric cone.

        zxray = (
            np.array(
                [
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    72.817,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    82.332,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -77.254,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                    -66.881,
                ]
            )
            / 100.0
        )  # Converted to m

        rxray = (
            np.array(
                [
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    234.881,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.206,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    231.894,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                    234.932,
                ]
            )
            / 100.0
        )  # Converted to m

    line_len = 3  # m  Make this long enough to go past the box for all chords.

    phi = np.array([60, 75])[(zxray > 0).astype(int)] * -np.pi / 180.0  # Convert to CCW radians
    fan = np.array(['Lower', 'Upper'])[(zxray > 0).astype(int)]
    fan_offset = np.array([0, int(len(rxray) // 2)])[(zxray < 0).astype(int)].astype(int)

    for i in range(len(zxray)):
        cnum = i + 1 - fan_offset[i]
        ods['bolometer']['channel'][i]['identifier'] = '{}{:02d}'.format(fan[i][0], cnum)
        ods['bolometer']['channel'][i]['name'] = '{} fan ch#{:02d}'.format(fan[i], cnum)
        cls = ods['bolometer']['channel'][i]['line_of_sight']  # Shortcut
        cls['first_point.r'] = rxray[i]
        cls['first_point.z'] = zxray[i]
        cls['first_point.phi'] = phi[i]
        cls['second_point.r'] = rxray[i] + line_len * np.cos(xangle[i])
        cls['second_point.z'] = zxray[i] + line_len * np.sin(xangle[i])
        cls['second_point.phi'] = cls['first_point.phi']

    return {'postcommands': ['trim_bolometer_second_points_to_box(ods)']}


@make_available_if(compare_version(imas_version, '3.25.0') >= 0)  # Might actually be 3.24.X. Close enough for now.
def setup_langmuir_probes_hardware_description_d3d(ods, shot):
    """
    Load DIII-D Langmuir probe locations into an ODS

    :param ods: ODS instance

    :param shot: int

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    import MDSplus

    if compare_version(ods.imas_version, '3.25.0') < 0:
        printe('langmuir_probes.embedded requires a newer version of IMAS. It was added by 3.25.0.')
        printe('ABORTED setup_langmuir_probes_hardware_description_d3d due to old IMAS version.')
        return {}

    tdi = r'GETNCI("\\langmuir::top.probe_*.r", "LENGTH")'
    # "LENGTH" is the size of the data, I think (in bits?). Single scalars seem to be length 12.
    printq('Setting up Langmuir probes hardware description, shot {}; checking availability, TDI={}'.format(shot, tdi))
    m = OMFITmdsValue(server='DIII-D', shot=shot, treename='LANGMUIR', TDI=tdi)
    try:
        data_present = m.data() > 0
    except MDSplus.MdsException:
        data_present = []
    nprobe = len(data_present)
    printq('Looks like up to {} Langmuir probes might have valid data for {}'.format(nprobe, shot))
    j = 0
    for i in range(nprobe):
        if data_present[i]:
            r = OMFITmdsValue(server='DIII-D', shot=shot, treename='langmuir', TDI=r'\langmuir::top.probe_{:03d}.r'.format(i))
            chk = r.check(debug=True, check_dim_of=-1)  # Don't check dimensions on these data
            if chk['result'] and r.data() > 0:
                # Don't bother gathering more if r is junk
                z = OMFITmdsValue(server='DIII-D', shot=shot, treename='langmuir', TDI=r'\langmuir::top.probe_{:03d}.z'.format(i))
                pnum = OMFITmdsValue(server='DIII-D', shot=shot, treename='langmuir', TDI=r'\langmuir::top.probe_{:03d}.pnum'.format(i))
                label = OMFITmdsValue(server='DIII-D', shot=shot, treename='langmuir', TDI=r'\langmuir::top.probe_{:03d}.label'.format(i))
                printq('  Probe i={i:}, j={j:}, label={label:} passed the check; r={r:}, z={z:}'.format(**locals()))
                ods['langmuir_probes.embedded'][j]['position.r'] = r.data()[0]
                ods['langmuir_probes.embedded'][j]['position.z'] = z.data()[0]
                ods['langmuir_probes.embedded'][j]['position.phi'] = np.NaN  # Didn't find this in MDSplus
                ods['langmuir_probes.embedded'][j]['identifier'] = 'PROBE_{:03d}: PNUM={}'.format(i, pnum.data()[0])
                ods['langmuir_probes.embedded'][j]['name'] = str(label.data()[0]).strip()
                j += 1
            else:
                printq('Probe i={i:}, j={j:}, r={r:} failed the check with chk={chk:}'.format(**locals()))
    return {}

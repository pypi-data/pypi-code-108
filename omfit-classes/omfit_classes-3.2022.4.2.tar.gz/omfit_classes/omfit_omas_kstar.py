"""
Functions for adding KSTAR data to the IMAS schema by writing to ODS instances
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
from omfit_classes.omfit_mds import OMFITmds, OMFITmdsValue
from omfit_classes.utils_base import compare_version
from omfit_classes.omfit_omas_utils import ensure_consistent_experiment_info

# noinspection PyBroadException
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


# Data inspection utilities
@make_available
def find_active_kstar_probes(shot, allowed_probes=None):
    """
    Serves LP functions by identifying active probes (those that have actual data saved) for a given shot

    Sorry, I couldn't figure out how to do this with a server-side loop over all
    the probes, so we have to loop MDS calls on the client side. At least I
    resampled to speed that part up.

    This could be a lot faster if I could figure out how to make the GETNCI
    commands work on records of array signals.

    :param shot: int

    :param allowed_probes: int array
        Restrict the search to a certain range of probe numbers to speed things up

    :return: list of ints
    """
    print(f'Searching for active KSTAR probes in shot {shot}...')
    omv_kw = dict(server='KSTAR', shot=shot, treename='KSTAR')
    lp_paths_unfiltered = OMFITmdsValue(TDI=r'GETNCI("\\TOP.ELECTRON.ELPA:EP*", "MINPATH")', **omv_kw).data()
    lp_paths = [lpp.strip() for lpp in lp_paths_unfiltered if re.match('[0-9]', lpp.strip().split(':')[-1][2:])]
    print(f'{len(lp_paths)} possible probes found')
    lp_nums = np.array([int(lpp.strip().split(':')[-1][2:]) for lpp in lp_paths])
    idx = lp_nums.argsort()
    lp_nums = lp_nums[idx]
    lp_paths = np.array(lp_paths)[idx]
    if allowed_probes is None:
        acceptable_probe_numbers = lp_nums
        acceptable_paths = lp_paths
    else:
        acceptable_probe_numbers = np.array([lpn for lpn in lp_nums if lpn in allowed_probes])
        acceptable_paths = np.array([lp_paths[i] for i in range(len(lp_nums)) if lp_nums[i] in allowed_probes])
        print(f'{len(acceptable_paths)} candidates remain after limiting search to only some specific probes.')
    valid = [None] * len(acceptable_paths)
    i = wd = tc = 0
    for i in range(len(acceptable_paths)):
        ascii_progress_bar(
            i,
            0,
            len(acceptable_paths),
            mess=f'Checking KSTAR#{shot} LP probes for valid data {lp_paths[i]} valid={valid[i]}; '
            f'probes with valid data so far = {wd}/{tc}',
        )
        valid[i] = OMFITmdsValue(TDI=f'resample({acceptable_paths[i]}.FOO, 0, 1, 1)', **omv_kw).check()
        wd = np.sum(np.array(valid).astype(bool))
        tc = len([a for a in valid if a is not None])
    ascii_progress_bar(
        i + 1,
        0,
        len(acceptable_paths),
        mess=f'Checked KSTAR#{shot} LP probes for valid data and found {wd} out of {tc} probes have valid data.',
    )
    print()
    return acceptable_probe_numbers[np.array(valid).astype(bool)]


# Data loading tools
# noinspection PyBroadException
@make_available_if(compare_version(imas_version, '3.25.0') >= 0)  # Might actually be 3.24.X. Close enough for now.
def load_data_langmuir_probes_kstar(ods, shot, probes=None, allowed_probes=None, tstart=0, tend=10, dt=0.0002, overwrite=False):
    """
    Downloads LP probe data from MDSplus and loads them to the ODS

    :param ods: ODS instance

    :param shot: int

    :param probes: int array-like [optional]
        Integer array of KSTAR probe numbers.
        If not provided, find_active_kstar_probes() will be used.

    :param allowed_probes: int array-like [optional]
        Passed to find_active_kstar_probes(), if applicable.
        Improves speed by limiting search to a specific range of probe numbers.

    :param tstart: float
        Time to start resample (s)

    :param tend: float
        Time to end resample (s)
        Set to <= tstart to disable resample

    :param dt: float
        Resample interval (s)
        Set to 0 to disable resample

    :param overwrite: bool
        Download and write data even if they already are present in the ODS.

    :return: ODS instance
        The data are added in-place, so catching the return is probably unnecessary.
    """

    # Make sure the ODS is for the right device/shot
    device = 'KSTAR'
    ensure_consistent_experiment_info(ods, device, shot)

    # Make sure the ODS already has probe positions in it
    try:
        assert is_numeric(ods['langmuir_probes.embedded[0].position.r'])
        assert ods['langmuir_probes.embedded[0].name'] == '1'
    except Exception:
        setup_langmuir_probes_hardware_description_kstar(ods, shot)

    # Select probes to gather
    probes = probes or find_active_kstar_probes(shot, allowed_probes=allowed_probes)

    do_resample = (dt > 0) and (tend > tstart)

    i = 0
    for i, probe in enumerate(probes):
        p_idx = probe - 1
        tdi = rf'\TOP.ELECTRON.ELPA:EP{probe}.FOO'  # Sorry, there doesn't seem to be a pointname for uncertainty.

        ascii_progress_bar(i, 0, len(probes), mess=f'Loading {device}#{shot} LP probe data ({probe}, {tdi})')

        if not overwrite:
            try:
                _ = ods['langmuir_probes.embedded'][p_idx]['time']
                _ = ods['langmuir_probes.embedded'][p_idx]['ion_saturation_current.data']
            except Exception:
                pass
            else:
                printd(f'Skipping probe {probe} with index {p_idx} because it already has data')
                continue

        if do_resample:
            tdi = f'resample({tdi}, {tstart}, {tend}, {dt})'
        m = OMFITmdsValue(server=device, shot=shot, treename='KSTAR', TDI=tdi)
        if m.check():
            # TODO: deal with calibrations and units; this is definitely a real signal that looks like it's
            # proportional to A, but that doesn't mean a factor isn't missing.
            ods['langmuir_probes.embedded'][p_idx]['time'] = m.dim_of(0)
            ods['langmuir_probes.embedded'][p_idx]['ion_saturation_current.data'] = m.data()  # Just nominal values

    ascii_progress_bar(i + 1, 0, len(probes), mess=f'Loaded {device}#{shot} LP probe data')

    return ods


# Hardware descriptor functions
@make_available_if(compare_version(imas_version, '3.25.0') >= 0)  # Might actually be 3.24.X. Close enough for now.
def setup_langmuir_probes_hardware_description_kstar(ods, shot):
    """
    Load KSTAR Langmuir probe locations into an ODS

    :param ods: ODS instance

    :param shot: int

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """
    import MDSplus

    # Is it okay to try this?
    if compare_version(ods.imas_version, '3.25.0') < 0:
        printe('langmuir_probes.embedded requires a newer version of IMAS. It was added by 3.25.0.')
        printe('ABORTED setup_langmuir_probes_hardware_description_kstar due to old IMAS version.')
        return {}

    # Reused items; set once
    ucf = 1e-3  # Unit Conversion Factor: mm to m
    omv_kw = dict(server='KSTAR', shot=shot, treename='KSTAR')
    base = r'\\TOP.ELECTRON.ELPA:EP*'

    # Get probe numbers from paths in MDSplus
    lp_paths_unfiltered = OMFITmdsValue(TDI=rf'GETNCI("{base}", "MINPATH")', **omv_kw).data()
    lp_paths = [lpp for lpp in lp_paths_unfiltered if re.match('[0-9]', lpp.strip().split(':')[-1][2:])]
    lp_numbers = np.array([int(lpp.strip().split(':')[-1][2:]) for lpp in lp_paths])
    nprobe = len(lp_numbers)

    # Get probe coordinates
    r = OMFITmdsValue(TDI=rf'GETNCI("{base}.R", "RECORD")', **omv_kw).data()
    z = OMFITmdsValue(TDI=rf'GETNCI("{base}.Z", "RECORD")', **omv_kw).data()
    phi = OMFITmdsValue(TDI=rf'GETNCI("{base}.TOR_ANGLE", "RECORD")', **omv_kw).data()
    side_area = OMFITmdsValue(TDI=rf'GETNCI("{base}.NA", "RECORD")', **omv_kw).data()

    # Verify data integrity
    assert len(r) == nprobe, f'Arrays should be length {nprobe} (based on probe#), but R has length {len(r)}'
    assert len(z) == nprobe, f'Arrays should be length {nprobe} (based on probe#), but Z has length {len(z)}'
    assert len(phi) == nprobe, f'Arrays should be length {nprobe} (based on probe#), but phi has length {len(phi)}'
    assert len(side_area) == nprobe, f'Expected len(side_area)={nprobe} (based on probe#), not {len(side_area)}'

    # Sort
    idx = lp_numbers.argsort()
    lp_numbers = lp_numbers[idx]
    r = r[idx]
    z = z[idx]
    phi = phi[idx]
    side_area = side_area[idx]
    # Only the side area is recorded in MDSplus. If it matches data I got from Jun-Gyo BAK, then assume
    # that the top area also matches. Otherwise, we don't know the top area.
    top_area = np.empty(nprobe)
    top_area[:] = np.NaN
    top_area[np.isclose(side_area, 4.088e-6, atol=1e-12)] = 2.827e-5  # m^2

    # Load
    for i in range(nprobe):
        ods['langmuir_probes.embedded'][i]['position.r'] = r[i] * ucf
        ods['langmuir_probes.embedded'][i]['position.z'] = z[i] * ucf
        ods['langmuir_probes.embedded'][i]['position.phi'] = phi[i] * np.pi / 180.0
        # Is having the surface area without the B-field confusing? One cannot just divide by this area
        # to get J_sat; additional transformations are needed.
        ods['langmuir_probes.embedded'][i]['surface_area'] = top_area[i]
        # TODO: Add side surface area, too, if that gets added (see https://jira.iter.org/browse/IMAS-3311)
        ods['langmuir_probes.embedded'][i]['name'] = lp_numbers[i]

    # It should be possible to add surface area as well, but information about angles is needed.

    # From Jun-Gyo BAK at KSTAR:
    # 1. The projected area (of the probe tip) for the normal incidence ( 90 degree )
    # S_1= 2.827 E-5 m^2
    # 2. The projected area for incidence angle of 0 degree
    # S_2= 4.088 E-6 m^2
    # S ~ (S_1*sin(theta) + S_2*cos(theta))
    # Here, theta (incidence angle ) was assumed as 5 degree
    # Thus, J_sat = I_sat/S

    # So, we need the angle between the probe tip and the field.
    # S_2 is recorded in MDSplus as NA. Any probe that has NA = 4.088e-06 m^2
    # should be safe to assume has S_1 = 2.827e-5 m^2, S_2 = 4.088e-6 m^2.
    # Add to langmuir_probes.embedded[:].surface_area

    return {}

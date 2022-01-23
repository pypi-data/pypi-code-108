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

from omfit_classes.utils_fusion import tokamak, is_device
from omfit_classes.utils_math import line_intersect
from omfit_classes.utils_base import compare_version
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_eqdsk import gEQDSK_COCOS_identify, OMFITgeqdsk
from omfit_classes.exceptions_omfit import doNotReportException as DoNotReportException

import os
import numpy as np
import glob
import omas
from scipy.interpolate import interp1d
from omas import *
from matplotlib import pyplot as plt

__all__ = [
    'add_generic_OMFIT_info_to_ods',
    'add_experiment_info_to_ods',
    'ensure_consistent_experiment_info',
    'setup_hardware_overlay_cx',
    'toray_to_omas',
    'nubeam_to_omas',
    'add_hardware_to_ods',
    'multi_efit_to_omas',
    'pf_coils_to_ods',
    'make_sample_ods',
    'transp_ic_to_omas',
    'setup_magnetics_hardware_description_general',
    'select_mag_probe_template',
    'get_shape_control_points',
    'setup_position_control_hardware_description_general',
    'setup_pulse_schedule_hardware_description_general',
    'classify_ods_eq_topology',
    'get_strike_point',
    'OmasUtilsBadInput',
    'orthogonal_distance',
    'load_sample_eq_specifications',
    'GradeEquilibrium',
]


class OmasUtilsBadInput(ValueError, DoNotReportException):
    """Bad inputs were used to a method in omfit_omas_utils.py"""


# OMAS extra structures
# Based on https://github.com/gafusion/OMFIT-source/blob/unstable/omfit/omfit_classes/fluxSurface.py#L3122-L3167
_extra_structures = {
    'pulse_schedule': {
        'pulse_schedule.position_control.flux_gates': {
            "data_type": "STRUCT_ARRAY",
            "documentation": "Each so-called gate is a pair of points in (R,Z) between which "
            "a specified flux surface (by default, the separatrix) must pass. For example, "
            "the separatrix might need to pass through the entrance to a narrow structure in the "
            "divertor, or a flux surface a set distance into the SOL might need to also enter "
            "such a structure.",
            "full_path": "pulse_schedule/position_control/flux_gates",
        },
        'pulse_schedule.position_control.flux_gates[:].name': {
            "data_type": "STR_0D",
            "documentation": "Name or label for this gate",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/name",
        },
        'pulse_schedule.position_control.flux_gates[:].r1': {
            "data_type": "FLT_0D",
            "documentation": "R coordinate of first endpoint of the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/r1",
            "units": "m",
        },
        'pulse_schedule.position_control.flux_gates[:].r2': {
            "data_type": "FLT_0D",
            "documentation": "R coordinate of second endpoint of the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/r2",
            "units": "m",
        },
        'pulse_schedule.position_control.flux_gates[:].z1': {
            "data_type": "FLT_0D",
            "documentation": "Z coordinate of first endpoint of the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/z1",
            "units": "m",
        },
        'pulse_schedule.position_control.flux_gates[:].z2': {
            "data_type": "FLT_0D",
            "documentation": "Z coordinate of second endpoint of the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/z2",
            "units": "m",
        },
        'pulse_schedule.position_control.flux_gates[:].applies_to_psin': {
            "data_type": "FLT_1D",
            "documentation": "normalized psi values of flux surfaces that must pass through this gate."
            "If no flux surfaces are listed under any system, it is assumed that the psi_n = 1 (LCFS) "
            "surface must clear the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/applies_to_psin(:)",
        },
        'pulse_schedule.position_control.flux_gates[:].applies_to_dr_mid': {
            "data_type": "FLT_1D",
            "documentation": "Specify flux surfaces that must pass through this gate by giving the "
            "R value of their intersection with the outboard midplane, relative to the LCFS "
            "(the LCFS is 0, and 0.01 is 1 cm out into the SOL. "
            "If no flux surfaces are listed under any system, it is assumed that the psi_n = 1 (LCFS) "
            "surface must clear the gate.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/applies_to_dr_mid(:)",
            "units": "m",
        },
        'pulse_schedule.position_control.flux_gates[:].time_range': {
            "data_type": "FLT_1D",
            "documentation": "Specify the time range when this flux gate should be considered "
            "by providing the start and end of the range as a two element sequence. The gate applies "
            "to all times if this settings is missing or if the end time isn't after the start time.",
            "full_path": "pulse_schedule/position_control/flux_gates(igate)/time_range(:)",
            "units": "s",
        },
    }
}
if not hasattr(omas.omas_utils, '_extra_structures'):
    omas.omas_utils._extra_structures = {}
for _ids in _extra_structures:
    for _item in _extra_structures[_ids]:
        _extra_structures[_ids][_item]['lifecycle_status'] = 'omfit'
    omas.omas_utils._extra_structures.setdefault(_ids, {}).update(_extra_structures[_ids])


def add_generic_OMFIT_info_to_ods(ods, root=None):
    """
    This function will fill in information in the ``ids_properties``
    and ``code`` section of the input ``ods`` and return the updated ``ods``

    :param ods: An omas ods instance

    :param root: An OMFITmodule, from which to extract the commit

    :returns: The updated ods
    """
    if not len(ods.location):
        for ds in ods:
            if ds != 'dataset_description':
                add_generic_OMFIT_info_to_ods(ods[ds], root=root)
        return ods

    prop = ods['ids_properties']
    prop['source'] = 'OMFIT project: ' + OMFIT.filename
    prop['provider'] = OMFIT['MainSettings']['SETUP']['email']
    prop['creation_date'] = utils_base.now()

    code = ods['code']
    code['name'] = 'OMFIT'
    if root is not None:
        code['commit'] = root['SETTINGS']['MODULE']['commit']
        code['name'] = 'OMFIT %s module' % (root['SETTINGS']['MODULE']['ID'])
    else:
        code['commit'] = repo("log -1 --pretty='%H'").strip()
    code['version'] = repo('describe')
    code['repository'] = ':'.join([socket.gethostname(), OMFITsrc])

    # this might be time dependent # code['output_flag'] = -1 # This means to not use this data; change to 0 to start using
    return ods


def add_experiment_info_to_ods(ods, root=None):
    """
    This function will fill in information in the `info` about the machine/pulse

    :param ods: An omas ods instance

    :param root: An OMFITmodule, from which to extract the machine/pulse info

    :returns: The updated ods
    """

    # add machine/pulse info
    if root is not None:
        experiment = root['SETTINGS']['EXPERIMENT']
    else:
        experiment = OMFIT['MainSettings']['EXPERIMENT']
    ods['dataset_description.data_entry.machine'] = experiment['device']
    ods['dataset_description.data_entry.pulse'] = experiment['shot']

    return ods


def ensure_consistent_experiment_info(ods, device, shot):
    """
    Ensures that the ODS, device, and shot are consistent

    If machine or pulse are not set, they are set to the provided device / shot.
    If they are set but inconsistent, AssertionError is raised.

    :param ods: ODS instance

    :param device: str

    :param shot: int
    """
    machine = ods['dataset_description.data_entry'].setdefault('machine', tokamak(device))
    pulse = ods['dataset_description.data_entry'].setdefault('pulse', shot)
    assert is_device(
        ods['dataset_description.data_entry.machine'], device
    ), f"This ODS is for a different device ({machine}). We shouldn't load {device} data here."
    assert (
        ods['dataset_description.data_entry.pulse'] == shot
    ), f"This ODS is for a different shot ({pulse}). We shouldn't load {shot} data here."


def add_hardware_to_ods(ods, device, pulse, hw_sys, overwrite=False):
    """
    Adds a single hardware system's info to an ODS (operates in place)

    :param ods: ODS instance

    :param device: string

    :param pulse: int

    :param hw_sys: string

    :param overwrite: bool

    :return: updated ods
    """
    device = tokamak(device, output_style='GPEC').lower()
    printd(f'Adding hardware to ODS; device = {device}, pulse = {pulse}, hw_sys = {hw_sys}', topic='omfit_omas')

    if not check_okay_to_write(ods, hw_sys, overwrite=overwrite):
        printw('Hardware location data for {} already in ODS. Skipping.'.format(hw_sys))
        return

    if hw_sys in ['magnetics', 'pulse_schedule', 'position_control']:
        setup_function_name = f'setup_{hw_sys}_hardware_description_general'
        setup_func_kw = {'device': tokamak(device)}
    else:
        setup_function_name = f"setup_{hw_sys}_hardware_description_{device}"
        exec(f'from omfit_classes.omfit_omas_{device} import {setup_function_name}', globals(), locals())
        setup_func_kw = {}
    setup_function = eval(setup_function_name, globals(), locals())

    printd('Setting up hardware description for {}...'.format(hw_sys))
    epilogue = setup_function(ods, pulse, **setup_func_kw)
    for postcommand in epilogue.get('postcommands', []):
        eval(postcommand)

    return ods


def interpret_strike_point(eqi, lower_bias=None):
    """
    Handles differences in recording strike point positions as RVSOUT, etc. vs RVSOD, etc.

    Determines whether the equilibrium is upper or lower biased to set which of the (upper/lower)
    strike point sets is connected to the primary separatrix. Then finds whichever definition exists
    and uses it to define as much as possible of the missing defintion. That is, if RVSOUT, ZVSOUT is
    provided and ZXPT1 < 0, then RVSOD = RVSOUT, ZVSOD = ZVSOUT, etc.

    We'll call these the OD definition (RVSOD) and the OI definition (RVSOUT/RVSIN).

    :param eqi: dict
        Dictionary of equilibrium information.
        Must contain one of the strike point definitions as well as ZXPT1.

    :param lower_bias: bool [optional]
        Backup plan in case you don't have ZXPT1 but you want the translation to be
        done for an upper/lower biased plasma, anyway.

    :return: dict
        The same dictionary that is input.
        Items are filled in in-place, so catching the return is not necessary.
    """
    if eqi is None:
        printd('Unable to interpret stirke point data with no equilibrium information.')
        return eqi
    eqi_upper = {k.upper(): v for k, v in eqi.items()}

    t = eqi_upper['ATIME']
    blank = np.empty(len(t))
    blank[:] = np.NaN

    # Determine which definition(s) are defined
    ou_req_keys = [f'RVSOU', f'ZVSOU', f'RVSIU', f'ZVSIU']
    od_req_keys = [f'RVSOD', f'ZVSOD', f'RVSID', f'ZVSID']
    oi_req_keys = ['RVSOUT', 'ZVSOUT', 'RVSIN', 'ZVSIN']
    ou_defined = all([k.upper() in eqi_upper and eqi_upper[k.upper()] is not None for k in ou_req_keys])
    od_defined = all([k.upper() in eqi_upper and eqi_upper[k.upper()] is not None for k in od_req_keys])
    oi_defined = all([k.upper() in eqi_upper and eqi_upper[k.upper()] is not None for k in oi_req_keys])

    # Prep output areas or make excuses and return early
    if (od_defined or ou_defined) and oi_defined:
        printd(
            'Both strike point definitions (RVSOUT,... and RVSOD,...) are already populated. '
            'There is no need to translate from one style to another.'
        )

        return eqi
    elif (od_defined or ou_defined) and not oi_defined:
        printd(
            'Using the RVSOD style strike point names to define RVSOUT style strike point names. '
            'A complete set of pointnames should be possible.'
        )
        eqi['RVSOUT'] = copy.copy(blank)
        eqi['ZVSOUT'] = copy.copy(blank)
        eqi['RVSIN'] = copy.copy(blank)
        eqi['ZVSIN'] = copy.copy(blank)
    elif not (od_defined or ou_defined) and oi_defined:
        printd(
            'Using the RVSOUT style strike point names to define RVSOD style strike point names. '
            'There is not enough information to define the secondary strike points this way.'
        )
        if eqi.get('RVSOD', None) is None:
            eqi['RVSOD'] = copy.copy(blank)
            eqi['ZVSOD'] = copy.copy(blank)
            eqi['RVSID'] = copy.copy(blank)
            eqi['ZVSID'] = copy.copy(blank)
        if eqi.get('RVSOU', None) is None:
            eqi['RVSOU'] = copy.copy(blank)
            eqi['ZVSOU'] = copy.copy(blank)
            eqi['RVSIU'] = copy.copy(blank)
            eqi['ZVSIU'] = copy.copy(blank)
    else:  # elif not od_defined and not oi_defined:
        printe(
            'Neither strike point defintion style (RVSOUT,... and RVSOD,...) is populated. '
            'There is no way to define either style of strike point position pointname.'
        )
        return eqi

    # Prepare information for picking upper vs lower bias
    zxpt1 = eqi_upper.get('ZXPT1', None)
    if zxpt1 is None:
        if lower_bias is None:
            raise ValueError(
                'Equilibrium information dictionary did not have enough information to '
                'translate between RVSOUT and RVSOD type strike point position pointnames.'
            )
        elif lower_bias:
            zxpt1 = -1 + t * 0
        else:
            zxpt1 = 1 + t * 0

    for i in range(len(t)):
        # Pick upper vs lower bias for this slice
        if zxpt1[i] <= 0:
            ud = 'D'
        else:
            ud = 'U'

        # Do the translation for this slice
        if (od_defined or ou_defined) and not oi_defined:
            for rz in 'RZ':
                for io, inout in zip(['I', 'O'], ['IN', 'OUT']):
                    eqi[f'{rz}VS{inout}'][i] = eqi_upper[f'{rz}VS{io}{ud}'][i]
        elif not od_defined and oi_defined:
            for rz in 'RZ':
                for io, inout in zip(['I', 'O'], ['IN', 'OUT']):
                    eqi[f'{rz}VS{io}{ud}'][i] = eqi_upper[f'{rz}VS{inout}'][i]

        # Replace R = 0 with NaN, because R = 0 is physically unreasonable and means failure to find the strike pt.
        for io, inout in zip(['I', 'O'], ['IN', 'OUT']):
            if not (eqi[f'RVS{inout}'][i] > 0):
                eqi[f'RVS{inout}'][i] = np.NaN
                eqi[f'ZVS{inout}'][i] = np.NaN
            for ud_ in 'UD':
                if not (eqi[f'RVS{io}{ud_}'][i] > 0):
                    eqi[f'RVS{io}{ud_}'][i] = np.NaN
                    eqi[f'ZVS{io}{ud_}'][i] = np.NaN

    return eqi


def filter_equilibrium_info_time_slices(eqi):
    """
    Given a dictionary of equilibrium information, perform filters to remove bad time-slices

    Bad is defined by 0 plasma current or 0 points in the boundary outline.
    The keys are case insensitive.

    :param eqi: dict
        Dictionary of equilibrium information. Must include 1D arrays:
            cpasma (plasma current in A)
            nbbbs (number of boundary points)

    :return: dict
        The updated equilibrium information dictionary
        The dictionary is edited in-place, so you don't have to catch the return
    """
    # Track how to handle quantities vs. time. Don't do AEQDSK because it has a different timebase.
    time_varying_1d = ['time', 'cpasma', 'bcentr', 'ssimag', 'ssibry', 'rmaxis', 'zmaxis', 'rzero', 'nbbbs']
    time_varying_2d = ['rhovn', 'rbbbs', 'zbbbs', 'qpsi', 'pres', 'ffprim', 'pprime', 'fpol']
    time_varying_3d = ['psirz']
    time_invariant = ['r', 'z', 'lim', 'rlim', 'zlim']

    # Prepare a dict with all lowercase keys
    eqi_lower = {}
    original_keys = {}
    for k, v in eqi.items():
        eqi_lower[k.lower()] = v
        original_keys[k.lower()] = k

    # Do the filtering
    wt = np.ones(len(eqi_lower['cpasma']), bool)  # Time-slice filter
    bad_slice = abs(eqi_lower['cpasma']) < 0.1  # A
    bad_slice |= eqi_lower['nbbbs'] == 0
    wt = ~bad_slice

    for quantity in time_varying_1d + time_varying_2d + time_varying_3d:
        if quantity in eqi_lower:
            if eqi_lower[quantity] is not None:
                eqi[original_keys[quantity]] = eqi_lower[quantity][wt]

    return eqi


def multi_efit_to_omas(device, pulse, efitid, ods=None, minimal=False, aeqdsk_time_diff_tol=0.1, no_empty=False, **kw):
    r"""
    Writes equilibrium data from MDSplus to ODS

    :param device: string

    :param pulse: int

    :param efitid: string

    :param ods: ODS instance
        A New ODS will be created if this is None

    :param minimal: bool
        Only gather and add enough data to run a cross-section plot

    :param aeqdsk_time_diff_tol: float
        Time difference in ms to allow between GEQDSK and AEQDSK time bases, in case they don't match exactly.
        GEQDSK slices where the closest AEQDSK time are farther away than this will not have AEQDSK data.

    :param no_empty: bool
        Remove empty GEQDSK slices from the result.
        Sometimes EFITs are loaded with a few invalid/empty slices (0 current,
        no boundary, all psi points = 0, etc.). This option will discard those slices
        before loading results into an ODS.

    :param \**kw: Additional keywords to read_basic_eq_from_mds()
        But not the quantities to gather as those are set explicitly in this function.

    :return: ODS instance
        The edit is done in-place, so you don't have to catch the output if you supply the input ODS
        On fail: empty ODS is returned
    """
    from omfit_classes.omfit_eqdsk import read_basic_eq_from_mds

    # Setup and gather --------------------------------------------------------------------------------------------
    if ods is None:
        ods = ODS()

    # Prepare for gathering
    gfq_essential = [
        'r',  # Needed for interpreting 2D psi grid
        'z',  # Needed for interpreting 2D psi grid
        'psirz',  # Primary measurement: 2D psi(r,z)  (actually 3D as funct of t, r, z)
        'lim',  # Primary measurement: limiting surface
        'rlim',  # Alternative to lim for some devices
        'zlim',  # Goes with Rlim; together they are an alternative for lim
        'rmaxis',  # Primary measurement: Magnetic axis coordinates
        'zmaxis',  # Primary measurement: Magnetic axis coordinates
        'rbbbs',  # Primary measurement: core plasma boundary outline
        'zbbbs',  # Primary measurement: core plasma boundary outline
        'nbbbs',  # Needed for interpreting core plasma boundary outline
        'ssimag',  # Needed for normalizing psirz
        'ssibry',  # Needed for normalizing psirz
        'rhovn',  # Primary measurement: square root of toroidal flux rho_N
        'qpsi',  # Primary measurement: safety factor q
        'bcentr',  # Needed for determining COCOS
        'cpasma',  # Needed for determining COCOS
    ]
    gfq_important = ['pres', 'ffprim', 'pprime', 'rzero', 'fpol']
    afq_x = ['RXPT1', 'ZXPT1', 'RXPT2', 'ZXPT2']
    afq_strike = ['{rz:}VS{io:}{ud:}'.format(rz=rz, io=io, ud=ud) for rz in 'RZ' for io in 'IO' for ud in 'UD']
    afq_strike += ['RVSOUT', 'RVSIN', 'ZVSOUT', 'ZVSIN']  # Some devices use these instead of RVSOD, etc.
    mfq_essential = []
    mfq_important = ['rrgam', 'zzgam', 'tangam', 'siggam', 'chigam', 'cmgam', 'fwtgam']
    derived_essential = ['time']
    derived_important = ['Br', 'Bz']

    if minimal:
        use_gfq = gfq_essential
        use_mfq = mfq_essential
        use_derived = derived_essential
    else:
        use_gfq = gfq_essential + gfq_important
        use_mfq = mfq_essential + mfq_important
        use_derived = derived_essential + derived_important

    # Get basic data
    eqi = read_basic_eq_from_mds(
        device=device,
        shot=pulse,
        tree=efitid,
        g_file_quantities=use_gfq,
        a_file_quantities=afq_x + afq_strike + ['atime'],
        measurements=use_mfq,
        derived_quantities=use_derived,
        **kw,
    )
    if eqi is None:
        printe('Try resetting SSH tunnels and gathering again.')
        return ods

    # Preliminary calculations ------------------------------------------------------------------------------------

    # Do some post-processing and filtering
    eqi = interpret_strike_point(eqi)
    if no_empty:
        eqi = filter_equilibrium_info_time_slices(eqi)

    # Use rho(psi_N) and psi_N(R, Z) to get rho(R, Z)
    nr = np.shape(eqi['r'])[-1]
    if eqi['rhovn'] is None:
        rho2d = None
    else:
        rho2d = np.zeros(np.shape(eqi['psirz']))
        for i in range(len(eqi['time'])):
            if eqi['ssimag'][i] == eqi['ssibry'][i]:
                # Dummy psi1d to prevent interpolation from failing completely. It'll be a junk answer either way.
                psi1d = np.linspace(eqi['ssimag'][i] - 0.1, eqi['ssimag'][i] + 0.1, nr)
            else:
                psi1d = np.linspace(eqi['ssimag'][i], eqi['ssibry'][i], nr)
            rho2d[i, :, :] = interp1d(psi1d, eqi['rhovn'][i, :], bounds_error=False, fill_value='extrapolate')(eqi['psirz'][i, :, :])

    # Deal with X-points
    blank = np.empty(len(eqi['time']))
    blank[:] = np.NaN
    rx1 = eqi['RXPT1'] if eqi['RXPT1'] is not None else blank
    zx1 = eqi['ZXPT1'] if eqi['ZXPT1'] is not None else blank
    rx2 = eqi['RXPT2'] if eqi['RXPT2'] is not None else blank
    zx2 = eqi['ZXPT2'] if eqi['ZXPT2'] is not None else blank

    badx1 = rx1 < 0
    badx2 = rx2 < 0
    rx1[badx1] = np.NaN
    zx1[badx1] = np.NaN
    rx2[badx2] = np.NaN
    zx2[badx2] = np.NaN

    # Load data to ODS --------------------------------------------------------------------------------------------

    # Load basic and global information
    ods['equilibrium.time'] = eqi['time'] / 1000  # ms to seconds
    ods['dataset_description.data_entry.pulse'] = pulse
    ods['dataset_description.ids_properties.comment'] = 'Equilibrium data loaded from {}#{}, EFIT tree = {}'.format(device, pulse, efitid)

    if (eqi['lim'] is None) and (eqi['rlim'] is not None) and (eqi['zlim'] is not None):
        # Some devices populate rlim and zlim instead of lim. We have to converge on a consistent convention.
        rlim = eqi['rlim']
        zlim = eqi['zlim']
        if len(np.shape(rlim)) == 2:
            # Some devices have stored the limiter at each time point, making it 2D vs time and space.
            # But we hope the limiter doesn't actually change vs time, so we'll ignore the time varaition.
            rlim = rlim[0, :]
            zlim = zlim[0, :]
        eqi['lim'] = np.array([rlim, zlim]).T

    if ('wall' not in ods) and (eqi['lim'] is not None):
        s = ods['wall.description_2d.0.limiter']
        s['type.description'] = 'first wall'
        s['type.name'] = 'first_wall'
        s['type.index'] = 0
        s['unit.0.outline.r'] = eqi['lim'][:, 0]
        s['unit.0.outline.z'] = eqi['lim'][:, 1]

    # Determine COCOS of gEQDSK data saved in MDS+
    native_cocos = gEQDSK_COCOS_identify(np.mean(eqi['bcentr']), np.mean(eqi['cpasma']))

    # Load data for each time slice
    with omas_environment(ods, cocosio=native_cocos):
        for i, t in enumerate(eqi['time']):
            if len(np.shape(eqi['r'])) == 2:
                rgrid = eqi['r'][i]
                zgrid = eqi['z'][i]
            else:
                rgrid = eqi['r']
                zgrid = eqi['z']
            s = ods['equilibrium.time_slice.{}'.format(i)]
            s['time'] = t / 1000.0  # ms to sec
            s['boundary.outline.r'] = eqi['rbbbs'][i, : int(eqi['nbbbs'][i])]
            s['boundary.outline.z'] = eqi['zbbbs'][i, : int(eqi['nbbbs'][i])]

            # aEQDSK data can be saved with a different time base than GEQDSK (thanks for that), so find a separate index.
            if 'atime' in eqi:
                dtga = abs(t - eqi['atime'])
                ia = dtga.argmin()
                if dtga[ia] > aeqdsk_time_diff_tol:
                    ia = None
            else:
                assert len(zx1) == len(
                    eqi['time']
                ), 'If no "atime" is available in equilibrium data, length of GEQDSK histories must match length of AEQDSK histories.'
                ia = i
            if ia is not None:
                # This GEQDSK slice has an AEQDSK slice that's within range, so put in the A data
                # X-points
                if zx1[ia] > 0 or zx2[ia] < 0:
                    # X-points are swapped: 1 is upper, 2 is lower. Load them in reverse.
                    s['boundary.x_point.0.r'] = rx2[ia]
                    s['boundary.x_point.0.z'] = zx2[ia]
                    s['boundary.x_point.1.r'] = rx1[ia]
                    s['boundary.x_point.1.z'] = zx1[ia]
                else:
                    # X-points are already in the preferred order: 1 is lower, 2 is upper.
                    s['boundary.x_point.0.r'] = rx1[ia]
                    s['boundary.x_point.0.z'] = zx1[ia]
                    s['boundary.x_point.1.r'] = rx2[ia]
                    s['boundary.x_point.1.z'] = zx2[ia]
                # Strike points
                for j, strike in enumerate(['VSOD', 'VSID', 'VSOU', 'VSIU']):
                    if eqi['R' + strike] is not None:
                        rval = eqi['R' + strike][ia]
                        zval = eqi['Z' + strike][ia]
                    else:
                        rval = zval = np.NaN
                    if rval > 0:
                        s['boundary.strike_point'][j]['r'] = rval
                        s['boundary.strike_point'][j]['z'] = zval
                    else:
                        s['boundary.strike_point'][j]['r'] = s['boundary.strike_point'][j]['z'] = np.NaN

            # gEQDSK data
            # ============0D
            s['global_quantities.magnetic_axis.r'] = eqi['rmaxis'][i]
            s['global_quantities.magnetic_axis.z'] = eqi['zmaxis'][i]
            s['global_quantities.psi_axis'] = eqi['ssimag'][i]
            s['global_quantities.psi_boundary'] = eqi['ssibry'][i]
            s['global_quantities.ip'] = eqi['cpasma'][i]

            # ============0D time dependent vacuum_toroidal_field
            if not minimal:
                ods['equilibrium.vacuum_toroidal_field.r0'] = eqi['rzero'][i]
            ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', i, eqi['bcentr'][i])

            # ============1D
            s['profiles_1d.psi'] = np.linspace(eqi['ssimag'][i], eqi['ssibry'][i], len(rgrid))
            if not minimal:
                s['profiles_1d.f'] = eqi['fpol'][i, :]
            if rho2d is not None:
                s['profiles_1d.phi'] = eqi['rhovn'][i, :] ** 2
                s['profiles_1d.rho_tor_norm'] = s['profiles_1d.rho_tor'] = eqi['rhovn'][i, :]
            if not minimal:
                s['profiles_1d.pressure'] = eqi['pres'][i, :]
                s['profiles_1d.f_df_dpsi'] = eqi['ffprim'][i, :]
                s['profiles_1d.dpressure_dpsi'] = eqi['pprime'][i, :]
            s['profiles_1d.q'] = eqi['qpsi'][i, :]

            # ============2D
            s['profiles_2d.0.psi'] = eqi['psirz'][i, :, :].T
            if rho2d is not None:
                s['profiles_2d.0.phi'] = (rho2d[i, :, :] ** 2).T
            s['profiles_2d.0.grid_type.index'] = 1
            s['profiles_2d.0.grid.dim1'] = rgrid
            s['profiles_2d.0.grid.dim2'] = zgrid
            if not minimal:
                if 'Br' in eqi:
                    s['profiles_2d.0.b_field_r'] = eqi['Br'][i, :, :].T
                if 'Bz' in eqi:
                    s['profiles_2d.0.b_field_z'] = eqi['Bz'][i, :, :].T

            # mEQDSK data
            # ============
            if not minimal and 'tangam' in eqi and 'rrgam' in eqi:
                # The array of channels can be padded with a bunch of empties at the end.
                valid_channels = np.where(abs(eqi['tangam'][i, :]) > 0)[0]
                if len(valid_channels):
                    lastchan_num = valid_channels[-1] + 1
                    for j in range(lastchan_num):
                        measured = unumpy.arctan(ufloat(eqi['tangam'][i, j], abs(eqi['siggam'][i, j])))
                        # unumpy.arctan was returning an object of type = uncertainties.core.AffineScalarFunc
                        measured = ufloat(nominal_values(measured), std_devs(measured))
                        s[f'constraints.mse_polarisation_angle.{j}.measured'] = measured
                        s[f'constraints.mse_polarisation_angle.{j}.reconstructed'] = np.arctan(eqi['cmgam'][i, j])
                        s[f'constraints.mse_polarisation_angle.{j}.time_measurement'] = t * 1e-3
                        s[f'constraints.mse_polarisation_angle.{j}.chi_squared'] = eqi['chigam'][i, j]
                        s[f'constraints.mse_polarisation_angle.{j}.weight'] = eqi['fwtgam'][i, j]
                        s[f'constraints.mse_polarisation_angle.{j}.source'] = f'mse.channel.{j}'

        # mEQDSK data
        # ============
        if not minimal and 'tangam' in eqi and 'rrgam' in eqi:
            # The array of channels can be padded with a bunch of empties at the end.
            valid_channels = np.where(np.sum(abs(eqi['tangam']), axis=0) > 0)[0]
            if len(valid_channels):
                lastchan_num = valid_channels[-1] + 1
                for j in range(lastchan_num):
                    ods[f'mse.channel.{j}.polarisation_angle.time'] = eqi['time'] * 1e-3
                    ods[f'mse.channel.{j}.polarisation_angle.data'] = unumpy.arctan(uarray(eqi['tangam'][:, j], abs(eqi['siggam'][:, j])))
                    ods[f'mse.channel.{j}.active_spatial_resolution.0.centre.r'] = eqi['rrgam'][0, j]
                    ods[f'mse.channel.{j}.active_spatial_resolution.0.centre.z'] = eqi['zzgam'][0, j]

    return ods


# The master setup / data loading function
def setup_hardware_overlay_cx(
    device,
    pulse=None,
    time=None,
    efitid='EFIT01',
    geqdsk=None,
    overwrite=False,
    default_load=True,
    minimal_eq_data=True,
    no_empty=False,
    **kw,
):
    r"""
    Sets up an OMAS ODS so that it can power a cross section view with diagnostic/hardware overlays. This involves
    looking up and writing locations of various hardware to the ODS.

    :param device: string
        Which tokamak?

    :param pulse: int
        Which pulse number? Used for gathering equilibrium and for looking up hardware configuration as it
        could vary with time.

    :param time: int or float array [optional]
        Time (ms) within the pulse, used for looking up equilibrium only
        If None and no gEQDSKs, try to get all times from MDSplus

    :param efitid: string
        EFIT SNAP file or ID tag in MDS plus: used for looking up equilibrium only

    :param geqdsk: OMFITgeqdsk instance (optional)
        Provides EFIT instead of lookup using device, pulse, time, efitid. efitid will be ignored completely. device
        and pulse will still be used to look up hardware configuration. time might be used. Providing inconsistent
        data may produce confusing plots.

    :param overwrite: bool
        Flag indicating whether it is okay to overwrite locations if they already exist in ODS

    :param default_load: bool
        Default action to take for loading a system. For example, \**kw lets you explicitly set gas_injection=False to
        prevent calling setup_gas_injection_hardware_description. But for systems which aren't specified, the default
        action (True/False to load/not load) is controlled by this parameter.

    :param minimal_eq_data: bool
        Skip loading all the equilibrium data needed to recreate GEQDSK files and only get what's needed for plots.

    :param no_empty: bool
        Filter out equilibrium time-slices that have 0 current or 0 boundary outline points.
        (this is passed to multi_efit_to_omas())

    :param \**kw: keywords dictionary
        Disable gathering/setup of data for individual hardware systems by setting them to False using their names
        within IMAS.
        For example: gas_injection=False will prevent the call to setup_gas_injection_hardware_description().

    :return: OMAS ODS instance containing the data you need to draw a cross section w/ diagnostic/hardware overlays.
    """
    quiet = kw.pop('quiet', False)

    def case_info_to_str(case_info):
        device_info = f" {case_info['device']}" if case_info['device'] is not None else ''
        shot_info = f"#{case_info['shot']}" if case_info['shot'] is not None else ''
        efitid_info = f" {case_info['efitid']}" if case_info['efitid'] is not None else ''
        return f"Equilibrium data from GEQDSK {device_info}{shot_info}{efitid_info}"

    # Equilibrium
    if (geqdsk is None) and (tolist(time)[0] is not None) and len(tolist(time)) == 1:
        # Single time
        assert pulse is not None, 'Must supply either valid gEQDSK or valid device, pulse, time, efitid (bad pulse)'
        assert time is not None, 'Must supply either valid gEQDSK or valid device, pulse, time, efitid (bad time)'
        assert efitid is not None, 'Must supply either valid gEQDSK or valid device, pulse, timeF, efitid (bad efitid)'
        geqdsk = OMFITgeqdsk('g{:06d}.{:05d}'.format(int(pulse), int(time))).from_mdsplus(
            device=device, shot=pulse, time=time, SNAPfile=efitid
        )
        ods = geqdsk.to_omas()
        ods['dataset_description.ids_properties.comment'] = 'Equilibrium data loaded from {}#{}, EFIT tree = {}'.format(
            device, pulse, efitid
        )
    elif geqdsk is None:
        # Load all times so we can switch quickly later
        ods = multi_efit_to_omas(device, pulse, efitid, minimal=minimal_eq_data, no_empty=no_empty)
    elif isinstance(geqdsk, OMFITgeqdsk):
        # Single time from single OMFITgeqdsk
        try:
            g_pulse = int(geqdsk['CASE'][3].split('#')[-1])
            g_time = float(geqdsk['CASE'][4].split('ms')[0])
        except KeyError:
            printw('Unable to confirm that g-file shot/time match other settings.')
        else:
            pulse, time = g_pulse, g_time
            print('pulse & time have been reassigned from geqdsk contents: pulse = {}, time = {}'.format(pulse, time))
        ods = geqdsk.to_omas()
        ods['dataset_description.ids_properties.comment'] = case_info_to_str(geqdsk.case_info())
    elif isinstance(geqdsk, dict):
        # Container that should have some OMFITgeqdsk instances
        g_keys = [k for k, v in geqdsk.items() if isinstance(v, OMFITgeqdsk)]
        if len(g_keys):
            ods = None
            for i, k in enumerate(g_keys):
                if ods is None:
                    ods = geqdsk[k].to_omas(time_index=i)
                else:
                    geqdsk[k].to_omas(ods=ods, time_index=i)
            ods['dataset_description.ids_properties.comment'] = case_info_to_str(geqdsk[g_keys[0]].case_info())
            case = geqdsk[g_keys[0]]['CASE']
            try:
                g_pulse = int(geqdsk[g_keys[0]]['CASE'][3].split('#')[-1])
                g_time = float(geqdsk[g_keys[0]]['CASE'][4].split('ms')[0])
            except KeyError:
                printw('Unable to confirm that g-file shot/time match other settings.')
            else:
                pulse, time = g_pulse, g_time

        else:
            raise OMFITexception(
                'No OMFITgeqdsk instances were found in the container! If you want to provide a dict-like object '
                'as geqdsk, it should contain some geqdsks!'
            )
    else:
        raise OMFITexception(
            f'Unrecognized type for geqdsk: ({type(geqdsk)}) . '
            f'Should be None to draw from device/shot in MDSplus, OMFITgeqdsk to use one equilibrium slice, '
            f'or dict-like containing OMFITgeqdsk instances to draw from a set of OMFITgeqdsks.'
        )

    ods['dataset_description.data_entry.machine'] = tokamak(device)
    ods['dataset_description.data_entry.pulse'] = pulse

    # Hardware

    # List subsets whose parent groups are going to be loaded; do not load these as it would be redundant
    subs = {'position_control': 'pulse_schedule'}
    dont_load = []
    for sub in subs.keys():
        if kw.get(subs[sub], default_load):
            dont_load += [sub]
    # Load hardware description data
    for hw_sys in omas.omas_utils.list_structures(ods.imas_version) + ['position_control']:
        if kw.pop(hw_sys, default_load) and hw_sys not in dont_load:
            add_hardware_to_ods(ods, device, pulse, hw_sys, overwrite=overwrite)
            if not quiet:
                print('Gathered data for hardware system: {}'.format(hw_sys))
        else:
            if not quiet:
                print('Skipped data gathering for hardware system: {}'.format(hw_sys))
    return ods


def check_okay_to_write(ods, hardware_name, overwrite=False):
    """
    Check the status of the ODS before you overwrite existing data you care about! Used while setting up hardware
    information for the cross section overlay (setup_hardware_overlay_cx)

    :param ods: OMAS ODS instance

    :param hardware_name: string
        Name of the sub ODS for the hardware system of interest, like 'thomson_scattering'

    :param overwrite: bool
        Is overwriting allowed if the ODS contains locations only? Actual data will not be overwritten, regardless.

    :return: bool
        Flag indicating that it's okay to write locations, either because there are none for this category yet, or
        because you indicated that overwriting locations only (not data) would be okay.
    """

    # Shortcuts to common position strings
    moving_pt = 'channel.0.position.r.data'  # Measures at point which moves over time
    los_chan = 'channel.0.line_of_sight.first_point.r'  # View-chord with some line-of-slight and 1st pt, etc.

    data_name = {  # Data quantity to check to determine whether or not the ODS has data for this hardware system
        'barometry': 'gauge.0.pressure.data',
        'bolometer': 'channel.0.power.data',
        'charge_exchange': 'channel.0.temperature.data',
        'ec_antennas': 'antenna.0.power.data',
        'ece': 'channel.0.t_e.data',
        'equilibrium': 'time_slice.0.profiles_2d.0.psi',
        'gas_injection': 'pipe.0.exit_position.flow_rate.data',
        'ic_antennas': 'antenna.0.power.data',
        'interferometer': 'channel.0.n_e_line.data',
        'magnetics': 'bpol_probe.0.field.data',
        'pf_active': 'coil.0.current.data',
        'thomson_scattering': 'channel.0.t_e.data',
        'langmuir_probes': 'embedded.0.ion_saturation_current.data',
    }.get(hardware_name, None)
    position = {  # Position quantity to check to determine whether or not the ODS has hardware geometry information
        'barometry': 'gauge.0.position.r',
        'bolometer': los_chan,
        'charge_exchange': moving_pt,
        'ec_antennas': 'antenna.0.launching_position.r.data',
        'ece': moving_pt,
        'equilibrium': 'time_slice.0.profiles_2d.0.grid.dim1',
        'gas_injection': 'pipe.0.exit_position.r',
        'ic_antennas': 'antennas.0.strap.0.geometry.geometry_type.r',  # "geometry_type" gets replaced
        'interferometer': los_chan,
        'magnetics': 'bpol_probe.0.position.r',
        'pf_active': 'coil.0.element.0.geometry.geometry_type.r',  # "geometry_type" gets replaced
        'thomson_scattering': 'channel.0.position.r',
        'langmuir_probes': 'embedded.0.position.r',
    }.get(hardware_name, None)
    geometry_type = {  # The string "geometry_type" in position will be replaced by something like "rectangle"
        'ic_antennas': 'antennas.0.strap.0.geometry.geometry_type',
        'pf_active': 'coil.0.element.0.geometry.geometry_type',
    }.get(hardware_name, None)

    # Avoid overwriting existing data
    try:
        has_data = ods[hardware_name][data_name] is not None
    except (ValueError, LookupError, TypeError):
        has_data = False
    if has_data:  # Writing new locations could produce inconsistency between T_e and R,Z data, so don't do it.
        print('This ODS already has {hw:} data loaded under {dat:}; skipping {hw:} location setup.'.format(hw=hardware_name, dat=data_name))
        return False
    printd("Checked ods['{hw:}']['{dat:}'] and didn't find anything to overwrite.".format(hw=hardware_name, dat=data_name))

    # Avoid overwriting existing hardware locations
    try:
        geo_type = ods[hardware_name][geometry_type]
    except (ValueError, LookupError, TypeError):
        geo_type = 'rectangle'  # As good a default as any.
        # The alternative to geo_type lookup would be checking through all possibilities: "rectangle", "oblique",
        # etc., but if geometry_type isn't filled out, the position info isn't complete, anyway, so why bother?
    try:
        has_locs = ods[hardware_name][position.replace('geometry_type', geo_type)] is not None
    except (ValueError, LookupError, TypeError, AttributeError):
        has_locs = False
    if has_locs and not overwrite:
        print(
            'This ODS already has {hw:} locations loaded under {pos:}; skipping {hw:} location setup '
            '(call again with overwrite=True to reload locations).'.format(hw=hardware_name, pos=position)
        )
        return False
    printd(
        "Checked ods['{hw:}']['{pos:}'] and didn't find anything to overwrite or overwrite was allowed.".format(
            hw=hardware_name, pos=position
        )
    )

    printd('Okay to write {} locations into ODS.'.format(hardware_name))
    return True


def get_first_wall(ods):
    """
    Search for limiters with type description indicating a first wall.
    This is a utility used in the course of setup_hardware_overlay_cx.

    :param ods: OMAS ODS instance

    :return: array
        r and z arrays for wall outline
    """
    desc = [ods['wall']['description_2d'][i]['limiter']['type']['description'] for i in ods['wall']['description_2d']]
    is_wall = [d in ['first wall', 'first_wall'] for d in desc]
    iwall = np.where(is_wall)[0][0]
    lim_outline = ods['wall']['description_2d'][iwall]['limiter']['unit'][0]['outline']
    return lim_outline


def trim_bolometer_second_points_to_box(ods, pad=None):
    """
    Trims second points in bolometer array so that they are on the edge of a box around the data.
    That is, assuming the bolometer setup script crudely defined the second points in sightlines using the first
    point, an angle, and a length that would be long enough to span the whole tokamak interior, we will have second
    points well outside of the vessel for most chords. That's the way efitviewer sets up its chords at first. This
    function cleans up the results of such a crude setup. Don't use if you already set up your bolometers carefully.

    This is a utility used in the course of setup_hardware_overlay_cx.

    :param ods: OMAS ODS instance

    :param pad: float
        Amount of padding around the outside of the extrema of the limiting surface (m). Set to None to auto pick.

    :return: None
        (the ODS is edited in-place)
    """

    # Pick a box around lim for the line endpoints
    lim_outline = get_first_wall(ods)
    box = np.array([lim_outline['r'].min(), lim_outline['z'].min(), lim_outline['r'].max(), lim_outline['z'].max()])
    pad = 0.125 * ((box[2] - box[0]) + (box[3] - box[1])) / 2.0 if pad is None else pad
    box += np.array([-pad, -pad, pad, pad])

    boxpath = np.array([[box[0], box[1]], [box[0], box[3]], [box[2], box[3]], [box[2], box[1]], [box[0], box[1]]])
    for i in range(len(ods['bolometer']['channel'])):
        cls = ods['bolometer']['channel'][i]['line_of_sight']
        ch_path = np.array([[cls['first_point.r'], cls['first_point.z']], [cls['second_point.r'], cls['second_point.z']]])
        intersections = line_intersect(boxpath, ch_path)
        dist = [(inter[0] - cls['first_point.r']) ** 2 + (inter[1] - cls['first_point.z']) ** 2 for inter in intersections]
        cls['second_point.r'], cls['second_point.z'] = intersections[np.array(dist).argmax()]
    return


def build_templates(template_file_search=os.sep.join([OMFITsrc, '..', 'modules', 'EFITtime', 'TEMPLATES', '*probe*'])):
    """
    Creates a namelist of magnetic probe descriptions based on data in TEMPLATES
    :param template_file_search: string
        Filename of file or files with wildcards allowed. Will be processed with glob.glob to get a list of files.
    :return: dict
        Returns a dict containing OMFITnamelist instances, each with probe data
    """
    from omfit_classes.omfit_namelist import OMFITnamelist

    d_templates = {}
    for template_file in glob.glob(template_file_search):
        file_root = '.'.join(os.path.split(template_file)[1].split('.')[:-1])
        d_templates[file_root] = OMFITnamelist(template_file)
    return d_templates


def select_mag_probe_template(device, shot, templates=None):
    """
    Selects and returns a magnetic probe information template. Used in chisquares plot.

    defaultVars parameters
    ----------------------
    :param device: string
        Which tokamak?

    :param shot: int
        Shot number used for looking up configuration in case it changed over time.

    :param templates: dict like [optional]
        dict or OMFITtree instance or similar containing templates. Within EFITtime, this is just root['TEMPLATES'].

    :return OMFITnamelist or None
        Returns a namelist with probe information (like R,Z coordinates, names, etc) if it can find one, otherwise None.
    """
    if templates is None:
        templates = build_templates()

    dprobe = None
    if is_device(device, 'DIII-D'):
        if shot:
            if shot < 112000:
                dprobe = templates['D3D_dprobe']
            elif 112000 <= shot < 156000:
                dprobe = templates['D3D_dprobe_112000']
            else:
                dprobe = templates['D3D_dprobe_156000']
    elif is_device(device, ('NSTX', 'NSTX-U')):
        dprobe = templates['NSTX_dprobe']
    else:
        raise RuntimeError(f"Missing dprobe.dat for device {device}")

    return dprobe


def setup_magnetics_hardware_description_general(ods, pulse, device=None):
    """
    Writes magnetic probe locations into ODS.

    :param ods: an OMAS ODS instance

    :param device: string
        Which tokamak?

    :param pulse: int

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """

    dprobe = select_mag_probe_template(device, pulse)
    if dprobe is None:
        printw('Warning: failed to look up magnetic probe configuration for device = {}, pulse = {}.'.format(device, pulse))
        return {}
    if compare_version(ods.imas_version, '3.25.0') >= 0:
        # TODO: check exact version number where bpol_probe changed to b_field_pol_probe. I know it's after 3.23.2
        bpol = 'b_field_pol_probe'  # This could change in later versions of the IMAS schema. Please update.
    else:  # IMAS schema 3.23.2 and earlier
        bpol = 'bpol_probe'

    nbp = len(dprobe['IN3']['XMP2'])
    for i in range(nbp):
        ods['magnetics'][bpol][i]['identifier'] = dprobe['IN3']['MPNAM2'][i]
        ods['magnetics'][bpol][i]['position.r'] = dprobe['IN3']['XMP2'][i]
        ods['magnetics'][bpol][i]['position.z'] = dprobe['IN3']['YMP2'][i]
        try:
            ods['magnetics'][bpol][i]['position.phi'] = float(dprobe['IN3']['MPNAM2'][i].strip()[-3:]) * np.pi / 180.0
        except ValueError:
            printd('Failed to read angle measurement for b_field_pol_probe {}'.format(dprobe['IN3']['MPNAM2'][i]))

    nfl = len(dprobe['IN3']['RSI'])
    for i in range(nfl):
        ods['magnetics.flux_loop'][i]['identifier'] = dprobe['IN3']['LPNAME'][i]
        ods['magnetics.flux_loop'][i]['position.0.r'] = dprobe['IN3']['RSI'][i]
        ods['magnetics.flux_loop'][i]['position.0.z'] = dprobe['IN3']['ZSI'][i]

    return {}


def get_boundary_plasma_and_limiter(dev=None, sh=None, efi=None, times_=None, gs=None, limiter_only=False, debug=False, debug_out=None):
    """
    Given gEQDSKs or instructions for looking up boundary & limiter information, get the plasma boundary and return it
    :param dev: string
    :param sh: int
    :param efi: string
    :param times_: float array
        Requested times. If g-files are provided, this is overruled and ignored.
        If this is not specified, the time base is read from data.
    :param gs: OMFITcollection instance containing gEQDSK instances as values and times as keys
        If this is provided, dev, sh, efi, and times_ are ignored.
    :param limiter_only: bool
        Skip gathering boundary; get limiter only. Should save time.
    :param debug: bool
    :param debug_out: dict-like [optional]
    :return: tuple
        (
            t: 1D float array (nt) of times in ms
            n: 1D int array (nt) of number of valid boundary points at each time
            r: 2D float array (nt * nb) of boundary R coordinates in m (time first, then index), padded with NaNs
            z: 2D float array (nt * nb) of boundary Z coordinates in m (time first, then index), padded with NaNs
            rlim: 1D float array (nlim) of limiter R vertices in m
            zlim: 1D float array (nlim) of limiter Z vertices in m
            xr: 2D float array (nt * 2) of X-point R positions in m. Secondary X-point might be NaN if it isn't found.
            xz: 2D float array (nt * 2) of X-point Z positions in m. X-point order is [bottom, top]
        )
        OR
        (
            rlim: 1D float array (nlim) of limiter R vertices in m
            zlim: 1D float array (nlim) of limiter Z vertices in m
        )
    """
    if debug_out is None and debug:
        debug_out = {}

    if gs is not None:
        # Option 1: provide a collection of G-files

        # Get limiter from the first G-file. Assume the limiter doesn't change in time.
        g0 = gs.values()[0]
        rlim_ = g0['RLIM']
        zlim_ = g0['ZLIM']
        if limiter_only:
            return rlim_, zlim_
        # Figure out dimensions and time base
        t_ = np.array(gs.keys())
        nt = len(t)
        n = gs['NBBBS']
        nmax = 0
        for tt in t_:
            valid = np.isfinite(gs[tt]['RBBBS']) & (gs[tt]['RBBBS'] > 0)
            nmax = np.max([nmax, np.sum(valid)])
        # Collect boundary
        r = np.empty((nt, nmax))
        r[:] = np.NaN
        z = copy.copy(r)
        for i, tt in enumerate(t_):
            r[i, : n[i]] = gs[tt]['RBBBS'][: n[i]]
            z[i, : n[i]] = gs[tt]['ZBBBS'][: n[i]]
        # Get x-point. If you want both X-points, you'll have to use a different method.
        xr1, xz1 = gs['fluxSurfaces']['info']['xpoint']
        xr2 = xz2 = np.array([np.NaN] * len(xr1))
        xr_ = np.array([xr1, xr2]).T
        xz_ = np.array([xz1, xz2]).T
    else:
        from omfit_classes.omfit_eqdsk import read_basic_eq_from_mds

        # Option 2: read a reduced data set from MDSplus
        assert dev is not None, 'Must provide a device if not providing collection of gEQDSKs'
        assert sh is not None, 'Must provide a shot number if not providing collection of gEQDSKs'
        assert efi is not None, 'Must provide an EFIT ID if not providing collection of gEQDSKs'

        # Gather and extract basic data
        info = read_basic_eq_from_mds(
            device=dev,
            shot=sh,
            tree=efi,
            derived_quantities=['time'],
            g_file_quantities=['RLIM', 'ZLIM', 'LIM'] + ([] if limiter_only else ['RBBBS', 'ZBBBS', 'NBBBS']),
            a_file_quantities=[] if limiter_only else ['RXPT1', 'ZXPT1', 'RXPT2', 'ZXPT2'],
        )
        if debug:
            debug_out['eq_info'] = info
        if info['LIM'] is None:
            rlim_ = info['RLIM']
            zlim_ = info['ZLIM']
        else:
            rlim_ = info['LIM'][:, 0]
            zlim_ = info['LIM'][:, 1]

        if limiter_only:
            return rlim_, zlim_

        n_ = info['NBBBS'].astype(int)
        r_ = info['RBBBS']
        z_ = info['ZBBBS']
        blank = np.empty(len(info['time']))
        blank[:] = np.NaN
        for thing in ['RXPT1', 'RXPT2', 'ZXPT1', 'ZXPT2']:
            if thing is None:
                info[thing] = blank
        xr_ = np.array([info['RXPT1'], info['RXPT2']]).T
        xz_ = np.array([info['ZXPT1'], info['ZXPT2']]).T

        # Handle time selection. Because the number of boundary points and their poloidal angles can change,
        # don't interpolate in time. Instead, just pick the nearest slice to each requested time.
        if times_ is None:
            treq = info['time']
        else:
            treq = times_
        nt = len(treq)
        nmax = n_.max()
        r = np.empty((nt, nmax))
        r[:] = np.NaN
        z = copy.copy(r)
        n = np.empty(nt)
        n[:] = np.NaN
        t_ = copy.copy(n)
        for i in range(nt):
            j = closestIndex(info['time'], treq[i])
            t_[i] = info['time'][j]
            n[i] = n_[j]
            r[i, : n_[i]] = r_[j, : n_[i]]
            z[i, : n_[i]] = z_[j, : n_[i]]

    n = n.astype(int)
    badx = (xr_ <= 0) | (xz_ <= -8)
    xr_[badx] = np.NaN
    xz_[badx] = np.NaN

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value encountered in .*')
        if (np.nanmean(xz_[:, 0]) > 0) or (np.nanmean(xz_[:, 1] < 0)):
            # X-points are in reverse order. Switch them so that bottom is first.
            xz_ = xz_[:, ::-1]
            xr_ = xr_[:, ::-1]

    if debug:
        debug_out['get_boundary_result'] = (t_, n, r, z, rlim_, zlim_, xr_, xz_)

    return t_, n, r, z, rlim_, zlim_, xr_, xz_


def get_shape_control_points(dev=None, sh=None, times_=None, debug=False, debug_out=None):
    """
    Gathers shape control points describing targets for the plasma boundary to intersect and returns them

    :param dev: string
    :param sh: int
    :param times_: float array [optional]
        Times to use. If provided, interpolate data. If not, auto-assign using first valid segment.
    :param debug: bool
    :param debug_out: dict-like [optional]
    :return: tuple
        (
            t: 1d float array (nt): times in ms (actual times used)
            r: 2d float array (nt * nseg): R coordinate in m of shape control points. Unused points are filled with NaN.
            z: 2d float array (nt * nseg): Z coordinate in m of shape control points
            rx: 2d float array (nt * 2): R coordinate in m of X points (2nd one may be NaN)
            rz: 2d float array (nt * 2): Z of X-points. Order is [bottom, top]
            rptnames: list of strings (nseg) giving labels for describing ctrl pts
            zptnames: list of strings (nseg) giving labels for describing ctrl pts
            list of 1D bool arrays vs. t giving validity of outer bottom, inner bottom, outer top, inner top strike pts
        )
    """

    assert dev is not None, 'Device must be specified in order to look up shape control data'
    assert sh is not None, 'Shot number must be specified in order to look up shape control data'
    if debug_out is None and debug:
        debug_out = {}

    if is_device(dev, 'DIII-D'):
        # Use this as a template. Copy and paste to set up other devices by adding elif ...
        segments = 18  # Maximum possible number of segments.
        first_segment = 1  # Starting number. Is the first segment 0 or 1?
        tree = None  # MDSplus treename
        r_format = 'EFSSEG{:02d}RT'  # r_format.format(segment_number) should give a valid MDSplus pointname
        z_format = 'EFSSEG{:02d}ZT'
        rx_format = 'EFSG{}RXT'  # Like r_format, but for the target X-point coordinate
        zx_format = 'EFSG{}ZXT'
        label_format = '{:02d}'
        # List pairs of poitnames for [top, bottom] divertor control method for double null isoflux control algorithms:
        dn_ctrl_method_pointnames = [['IDIXCTLTOP', 'IDIXCTLBOT']]
        # List ptnames that might be in use for single null algorithms; which one is defined depends on algorithm in use
        div_ctrl_method_pointnames = ['ISISPMTHD', 'IUISPMTHD']
        valid_ctrl_methods = [0]  # Values of strike point method must be in this list to be valid
        valid_outer_strike_methods = [1, 3]
        valid_inner_strike_methods = [2, 3]
        factor_to_get_meters = 1.0  # Data are multiplied by this to put them in m
        factor_to_get_ms = 1.0  # Independent variables / timebases are multiplied by this to put them in ms
    else:
        raise OMFITexception('Control point data are not (yet) provided for device {}.'.format(dev))
    if sh == 0:
        return None

    mkw = dict(server=dev, shot=sh, treename=tree)

    def get_dat(j0, j1, rf, zf, tt):
        """
        Shortcut for gathering target data
        :param j0: int
            Starting index (included as 1st element)
        :param j1: int
            Ending index (not included; last element will be this - 1)
        :param rf: string
            Format for determining TDI by filling in a number
        :param zf: string
            Format for determining TDI by filling in a number
        :param tt: float array [optional]
            Times in ms. If provided, data will be interpolated to this timebase.
            If None, the timebase will be picked up from the first valid segment.
        :return: tuple
            (
                t: 1D float array of actual times used in ms. Useful if input tt is None and times are auto-assigned.
                r: 2D float array (nt * nseg) giving time history of R coordinate in m for each segment; NaN for unused
                z: like R
            )
        """
        rr = []
        zz = []
        rm = None
        for j in range(j0, j1):
            rm = OMFITmdsValue(TDI=rf.format(j), **mkw)
            if (not rm.check()) or (abs(rm.data()).max() == 0):
                # Invalid data (fails check) or unused segment (all R=0)
                rr += [np.NaN]
                zz += [np.NaN]
            else:
                if tt is None:
                    tt = rm.dim_of(0)
                zm = OMFITmdsValue(TDI=zf.format(j), **mkw)
                if not zm.check():
                    # Invalid data (fails check)
                    rr += [np.NaN]
                    zz += [np.NaN]
                else:
                    r_ = interp1d(rm.dim_of(0) * factor_to_get_ms, rm.data(), bounds_error=False, fill_value=np.NaN)(tt)
                    z_ = interp1d(zm.dim_of(0) * factor_to_get_ms, zm.data(), bounds_error=False, fill_value=np.NaN)(tt)
                    rr += [r_ * factor_to_get_meters]
                    zz += [z_ * factor_to_get_meters]
        # Replace scalar placeholder NaN entries with arrays of NaNs matching length of tt.
        empty = np.empty(len(tt))
        empty[:] = np.NaN
        for j in range(len(rr)):
            if (len(np.atleast_1d(rr[j])) == 1) and np.isnan(np.atleast_1d(rr[j])):
                rr[j] = copy.copy(empty)
                zz[j] = copy.copy(empty)
        if debug:
            debug_out['rr_sample_get_dat'] = rr
            debug_out['rm_sample_get_dat'] = rm
            debug_out['tt_sample_get_dat'] = tt
        return tt, np.array(rr).T, np.array(zz).T

    times_, r, z = get_dat(first_segment, first_segment + segments, r_format, z_format, times_)
    times_, rx_0, zx_0 = get_dat(1, 3, rx_format, zx_format, times_)
    rptnames = zptnames = [label_format.format(i) for i in range(first_segment, first_segment + segments)]

    # Put X-points in the correct order
    rx_ = np.empty(np.shape(rx_0))
    rx_[:] = np.NaN
    zx_ = copy.copy(rx_)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value encountered in .*')
        top_first = (zx_0[:, 0] > 0) | (zx_0[:, 1] < 0)
        bot_first = (zx_0[:, 1] > 0) | (zx_0[:, 0] < 0)
    rx_[bot_first, :] = rx_0[bot_first, :]
    zx_[bot_first, :] = zx_0[bot_first, :]
    rx_[top_first, :] = rx_0[top_first, ::-1]
    zx_[top_first, :] = zx_0[top_first, ::-1]

    # Check X-point validity
    # Start with arrays of all-valid and then knock out times with invalid control methods.
    # For times or cases where the method cannot be determined, just ignore and let the X-point through.
    valid_xpt1 = np.ones(len(times_), bool)
    valid_xpt2 = np.ones(len(times_), bool)
    valid_outer_strike1 = copy.copy(valid_xpt1)
    valid_outer_strike2 = copy.copy(valid_xpt1)
    valid_inner_strike1 = copy.copy(valid_xpt1)
    valid_inner_strike2 = copy.copy(valid_xpt1)
    # First check single-null type control algorithms
    for dcmp in div_ctrl_method_pointnames:
        dcm = OMFITmdsValue(TDI=dcmp, **mkw)
        if not dcm.check():
            # Bad signal; move on. The pointname to use can vary depending on which algorithm is used.
            continue
        method = interp1d(dcm.dim_of(0), dcm.data(), bounds_error=False, fill_value=np.NaN)(times_)
        valid = np.nanmax(np.array([method == v for v in valid_ctrl_methods] + [np.isnan(method)]), axis=0)
        valid_xpt1 *= valid
        valid_xpt2 *= valid  # The second X-point probably doesn't even have a target defined, but let's just be sure.
        valid_os = np.nanmax(np.array([method == v for v in valid_outer_strike_methods] + [np.isnan(method)]), axis=0)
        valid_outer_strike1 *= valid_os
        valid_outer_strike2 *= valid_os
        valid_is = np.nanmax(np.array([method == v for v in valid_inner_strike_methods] + [np.isnan(method)]), axis=0)
        valid_inner_strike1 *= valid_is
        valid_inner_strike2 *= valid_is
    # Now double-null control algorithms
    for dcmps in dn_ctrl_method_pointnames:
        dcm_top = OMFITmdsValue(TDI=dcmps[0], **mkw)
        dcm_bot = OMFITmdsValue(TDI=dcmps[1], **mkw)
        if not (dcm_top.check() and dcm_bot.check()):
            # Unless we have both methods defined, move on.
            continue
        # Determine top and bottom X-point validity
        top_method = interp1d(dcm_top.dim_of(0), dcm_top.data(), bounds_error=False, fill_value=np.NaN)(times_)
        bot_method = interp1d(dcm_bot.dim_of(0), dcm_bot.data(), bounds_error=False, fill_value=np.NaN)(times_)
        nantop = np.isnan(top_method)
        nanbot = np.isnan(bot_method)
        # The + [nantop] or + [nanbot] is to include NaN in valid methods
        top_valid = np.nanmax(np.array([top_method == v for v in valid_ctrl_methods] + [nantop]), axis=0)
        bot_valid = np.nanmax(np.array([bot_method == v for v in valid_ctrl_methods] + [nanbot]), axis=0)
        top_os_valid = np.nanmax(np.array([top_method == v for v in valid_outer_strike_methods] + [nantop]), axis=0)
        bot_os_valid = np.nanmax(np.array([bot_method == v for v in valid_outer_strike_methods] + [nanbot]), axis=0)
        top_is_valid = np.nanmax(np.array([top_method == v for v in valid_inner_strike_methods] + [nantop]), axis=0)
        bot_is_valid = np.nanmax(np.array([bot_method == v for v in valid_inner_strike_methods] + [nanbot]), axis=0)
        # Map top X and bottom X to X1 and X2
        w1top = zx_[:, 0] > 0
        w2top = zx_[:, 1] > 0
        valid_xpt1[w1top] *= top_valid[w1top]
        valid_xpt1[~w1top] *= bot_valid[~w1top]
        valid_xpt2[w2top] *= top_valid[w2top]
        valid_xpt2[~w2top] *= bot_valid[~w2top]

        valid_outer_strike1[w1top] *= top_os_valid[w1top]
        valid_outer_strike1[~w1top] *= bot_os_valid[~w1top]
        valid_outer_strike2[w2top] *= top_os_valid[w2top]
        valid_outer_strike2[~w2top] *= bot_os_valid[~w2top]

        valid_inner_strike1[w1top] *= top_is_valid[w1top]
        valid_inner_strike1[~w1top] *= bot_is_valid[~w1top]
        valid_inner_strike2[w2top] *= top_is_valid[w2top]
        valid_inner_strike2[~w2top] *= bot_is_valid[~w2top]

    # Suppress Xpt targets for times with invalid divertor control methods (no direct X-point control)
    rx_[~valid_xpt1, 0] = np.NaN
    zx_[~valid_xpt1, 0] = np.NaN
    rx_[~valid_xpt2, 1] = np.NaN
    zx_[~valid_xpt2, 1] = np.NaN
    # Pack flags for valid strike points because we don't know which shape control points are strike points yet
    valid_strikes = [valid_outer_strike1, valid_inner_strike1, valid_outer_strike2, valid_inner_strike2]

    if debug:
        debug_out['valid_xpt1'] = valid_xpt1
        debug_out['valid_xpt2'] = valid_xpt2
        debug_out['get_control_points_result'] = (times_, r, z, rx_, zx_)

    return times_, r, z, rx_, zx_, rptnames, zptnames, valid_strikes


def flag_points_on_limiter(rlim_, zlim_, rc, zc, tolerance=0.0116, debug=False, debug_out=None):
    """
    Determines which control points are touching or outside of the limiting surface.
    These aren't part of the main plasma boundary control, but instead they are part of the divertor control solution.
    They should be analyzed separately for some purposes.

    :param rlim_: 1d float array (nlim)
        R coordinates of limiting surface in m
    :param zlim_: 1d float array (nlim)
        Z coordinates of limiting surface in m
    :param rc: 2d float array (nt * nseg)
        R coordinates of control points vs. time in m
    :param zc: 2d float array (nt * nseg)
        Z coordinates of control points vs. time in m
    :param tolerance: float
        Tolerance for distance between point and limiter, in m
    :param debug: bool
        Save stuff in a dict
    :param debug_out: dict-like [optional]
    :return: 1d bool array (nseg) flagging whether each control point is on the wall or not
    """

    try:
        import shapely.geometry
    except ImportError:
        shapely = None

    if debug_out is None and debug:
        debug_out = {}

    # It may be possible for a main plasma boundary point to briefly touch the wall if the plasma limits transiently,
    # but we don't expect it to maintain contact long-term. If a control point is on the main boundary, it won't
    # transition into being a divertor point unless there's a phase change. We don't want to deal with this right now,
    # so just please pick a time range that stays in the same phase.

    # Pick sample times
    nt = len(rc[:, 0])
    nseg = len(rc[0, :])
    nb = len(rlim_)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning, message='All-NaN slice encountered')
        rcm = np.nanmax(rc, axis=1)  # Consider control points that are used (not all NaNs)
    ii = np.arange(nt).astype(np.int64)  # Get a general index
    iavail = ii[~np.isnan(rcm)]  # Narrow available indices to times when control points aren't NaN
    na = len(iavail)
    isamp = ii[np.array([na // 3, na // 2, 2 * na // 3], np.int64)]  # 3 points near the middle of the valid set

    lim_curve = shapely.geometry.LineString([(rl, zl) for rl, zl in zip(rlim_, zlim_)])
    lim_poly = shapely.geometry.Polygon([(rl, zl) for rl, zl in zip(rlim_, zlim_)])

    on_limiter_ = np.zeros(nseg, bool)
    outside_lim_ = np.zeros(nseg, bool)

    if shapely is not None:
        # This way is about 7 times faster
        deviations = np.empty((len(isamp), nseg), float)
        deviations[:] = np.NaN
        for j in range(nseg):
            on_lim = []
            out_lim = []
            for ii, i in enumerate(isamp):
                if np.isnan(rc[i, j]) or np.isnan(zc[i, j]):
                    continue
                point = shapely.geometry.Point(rc[i, j], zc[i, j])
                out_lim += [not lim_poly.contains(point)]
                deviations[ii, j] = point.distance(lim_curve)
                if abs(deviations[ii, j]) < tolerance:
                    on_lim += [True]
                    break
            else:
                on_lim += [False]
            on_limiter_[j] = np.all(on_lim)  # A real limiter / divertor point would be limited on all of these.
            outside_lim_[j] = np.any(out_lim)
    else:
        # This way is clunky, but it doesn't require shapely, which OMFIT doesn't require
        skip_thresh = tolerance * 0.5
        on_limiter_ = np.zeros(nseg, bool)
        deviations = np.empty((len(isamp), nseg, nb))
        deviations[:] = np.NaN

        for j in range(nseg):
            on_lim = []
            for ii, i in enumerate(isamp):
                r = rc[i, j]
                z = zc[i, j]
                for k in range(nb - 1):
                    r0 = rlim_[k]
                    r1 = rlim_[k + 1]
                    z0 = zlim_[k]
                    z1 = zlim_[k + 1]
                    cross_product = (z - z0) * (r1 - r0) - (r - r0) * (z1 - z0)
                    if abs(cross_product) > skip_thresh:
                        # Cross product is so big it's not worth computing a deviation
                        continue
                    if (z1 == z0) and (r1 == r0):
                        deviation = np.sqrt((z - z1) ** 2 + (r - r1) ** 2)
                    else:
                        db = np.sqrt((z1 - z0) ** 2 + (r1 - r0) ** 2)
                        deviation = cross_product / db
                    deviations[ii, j, k] = deviation
                    if abs(deviation) <= tolerance:
                        on_lim += [True]
                        break
                else:
                    on_lim += [False]

            on_limiter_[j] = np.all(on_lim)  # A real limiter / divertor point would be limited on all of these.

    final_on_limiter = np.array(on_limiter_).astype(bool) | np.array(outside_lim_).astype(bool)
    if debug:
        debug_out['flag_lim_outside'] = outside_lim_
        debug_out['flag_lim_on_lim'] = on_limiter_
        debug_out['flag_points_on_limiter_result'] = final_on_limiter
        debug_out['flag_lim_isamp'] = isamp
        debug_out['flag_lim_deviations'] = deviations

    return final_on_limiter


def classify_ods_eq_topology(ods, dn_tolerance=0.001):
    """
    Figure out whether the shape is USN, LSN, or limited

    :param ods: ODS instance

    :param dn_tolerance: float
        Tolerance (in terms of normalized psi difference) for declaring a double null

    :return: 1D float array
        Flag indicating whether each equilibrium slice is LSN (-1), USN (+1), DN (0), or unknown/limited (np.NaN)
    """

    eq_time = ods['equilibrium.time']

    xr = ods['equilibrium.time_slice.:.boundary.x_point.:.r']
    xz = ods['equilibrium.time_slice.:.boundary.x_point.:.z']
    eqr = ods['equilibrium.time_slice'][0]['profiles_2d.0.grid.dim1']
    eqz = ods['equilibrium.time_slice'][0]['profiles_2d.0.grid.dim2']
    psirz = ods['equilibrium.time_slice.:.profiles_2d.0.psi']
    psia = ods['equilibrium.time_slice.:.global_quantities.psi_axis']
    psib = ods['equilibrium.time_slice.:.global_quantities.psi_boundary']
    dpsi = psib - psia
    psin = (psirz - psia[:, np.newaxis, np.newaxis]) / dpsi[:, np.newaxis, np.newaxis]
    topology = np.empty(len(eq_time))  # 0 is ~exact DN, 1 is USN, -1 is LSN, np.NaN is limited
    topology[:] = np.NaN
    for it in range(len(eq_time)):
        if np.any(~np.isnan(xr[it]) & ~np.isnan(xz[it])):
            xz_slice = xz[it, :]
            sel = ~np.isnan(xz_slice)
            xr_slice = xr[it, sel]
            xz_slice = xz_slice[sel]
            if len(xz_slice) == 1:
                topology[it] = np.sign(xz_slice[0])
            elif len(xz_slice) > 1:
                xpsin_ = RectBivariateSpline(eqr, eqz, psin[it, :, :])(xr_slice, xz_slice, grid=False)
                xidx = abs(xpsin_ - 1).argsort()
                xpsin = xpsin_[xidx]
                xz_sorted = xz_slice[xidx]
                if abs(xpsin[0] - xpsin[1]) < dn_tolerance:
                    topology[it] = 0
                else:
                    topology[it] = np.sign(xz_sorted[0] - xz_sorted[1])

    return topology


def get_strike_point(ods, in_out='outer', pri_sec='primary'):
    """
    Identify a specific strike point and get its coordinates

    It's easy to just pick a strike point, or even find inner-upper or outer-lower, but
    identifying primary-outer or primary-inner is a little harder to do. It's not clear
    that there's any consistent ordering of strike points that would trivialize this
    process, so this function exists to do it for you.

    :param ods: ODS instance

    :param in_out: str
        'outer': try to get an outer strike point (default)
        'inner': try to get an inner strike point

    :param pri_sec: str
        'primary': try to get a strike point connected to the primary X-point (default)
        'secondary': try to get a strike point connected with a secondary X-point

    :return: tuple
        time: 1D float array (s)
        r_strike: 1D float array (m)
        z_strike: 1D float array (m)
    """

    if pri_sec == 'secondary':
        pri_sec_flip = -1
    else:
        pri_sec_flip = 1

    eq_time = ods['equilibrium.time']
    r_strike_all = ods['equilibrium.time_slice.:.boundary.strike_point.:.r']
    z_strike_all = ods['equilibrium.time_slice.:.boundary.strike_point.:.z']
    topology = classify_ods_eq_topology(ods)

    preferred_strike_idx = np.empty(len(eq_time), int)
    preferred_strike_idx[:] = -1
    for it in range(len(eq_time)):
        if (topology[it] * pri_sec_flip) > 0:
            sel = z_strike_all[it, :] > 0
        elif (topology[it] * pri_sec_flip) < 0:
            sel = z_strike_all[it, :] < 0
        else:
            continue
        if in_out == 'inner':
            sel &= r_strike_all[it, :] == np.min(r_strike_all[it, sel])
        else:
            sel &= r_strike_all[it, :] == np.max(r_strike_all[it, sel])
        if sum(sel) == 1:
            preferred_strike_idx[it] = np.where(sel)[0][0]

    r_strike = r_strike_all[range(len(eq_time)), preferred_strike_idx]
    z_strike = z_strike_all[range(len(eq_time)), preferred_strike_idx]

    return eq_time, r_strike, z_strike


def select_critical_time_samples(t, x):
    """
    Identify samples that should be kept to allow information to be reconstructed trivially by linear interpolation

    :param t: 1D float array (nt)

    :param x: 2D array with first dimension matching t (nt * nx)

    :return: 1D bool array (nt)
    """
    dxdt = np.gradient(x, axis=0) / np.gradient(t)[:, np.newaxis]
    dx2 = np.gradient(dxdt, axis=0)
    keep_sample = ~np.product(dx2 == 0, axis=1).astype(bool)
    # Make sure the endpoints are always retained
    keep_sample[0] = True
    keep_sample[-1] = True
    printd('select_critical_time_samples identified {} out of {} points as critical'.format(np.sum(keep_sample), len(t)))
    return keep_sample


def setup_position_control_hardware_description_general(ods, shot, device=None, limiter_efit_id=None, debug=False, debug_out=None):
    """
    Loads DIII-D shape control data into the ODS

    :param ods: ODS instance

    :param shot: int

    :param device: string
        Only works for devices that have pointnames and other info specified. DIII-D should work.

    :param limiter_efit_id: string [optional]

    :param debug: bool

    :param debug_out: dict-like
        Catches debug output

    :return: dict
        Information or instructions for follow up in central hardware description setup
    """

    # Handle input keyword defaults
    if debug and debug_out is None:
        debug_out = {}

    # Set up shortcuts
    bry = ods['pulse_schedule.position_control.boundary_outline']
    xpt = ods['pulse_schedule.position_control.x_point']
    stk = ods['pulse_schedule.position_control.strike_point']

    # Fetch primary data: boundary outline and X-points
    t = None
    t, rctrl, zctrl, rx, zx, rptnames, zptnames, valid_strikes = get_shape_control_points(device, shot, t, debug=debug, debug_out=debug_out)
    # Suppress invalid values
    rzero = rctrl == 0
    rctrl[rzero] = np.NaN
    zctrl[rzero] = np.NaN

    # Get limiter
    try:
        rlim = ods['wall']['description_2d'][0]['limiter']['unit'][0]['outline']['r']
        zlim = ods['wall']['description_2d'][0]['limiter']['unit'][0]['outline']['z']
    except (KeyError, IndexError, ValueError):
        if limiter_efit_id is None:
            if is_device(device, 'DIII-D'):
                limiter_efit_id = 'EFITRT1'
            elif is_device(device, 'EAST'):
                limiter_efit_id = 'EFIT_EAST'
            else:
                raise ValueError('No rule for auto picking EFITID for device {}. Please specify limiter_efit_id.'.format(device))
        rlim, zlim = get_boundary_plasma_and_limiter(device, shot, limiter_efit_id, t, limiter_only=True, debug=True, debug_out=debug_out)
    if debug:
        debug_out['rlim'] = rlim
        debug_out['zlim'] = zlim

    # Distinguish boundary from strike points
    on_limiter = flag_points_on_limiter(rlim, zlim, rctrl, zctrl, debug=debug, debug_out=debug_out)

    # Compress
    clump = np.concatenate((rctrl, zctrl, rx, zx), axis=1)
    clump[np.isnan(clump)] = 0  # NaNs will ruin the diffs and != 0 checks
    keep_sample = select_critical_time_samples(t, clump)
    if debug:
        debug_out['t_before'] = copy.copy(t)
        debug_out['rx_before'] = copy.copy(rx[:, 0])
        debug_out['t_filtered'] = t[keep_sample]
        debug_out['rx_filtered'] = rx[keep_sample, 0]
    rctrl = rctrl[keep_sample, :]
    zctrl = zctrl[keep_sample, :]
    rx = rx[keep_sample, :]
    zx = zx[keep_sample, :]
    t = t[keep_sample]

    # Organize data
    rstrk = rctrl[:, on_limiter]
    zstrk = zctrl[:, on_limiter]
    rbdry = rctrl[:, ~on_limiter]
    zbdry = zctrl[:, ~on_limiter]
    rbpt = np.array(rptnames)[~on_limiter]
    zbpt = np.array(zptnames)[~on_limiter]
    rspt = np.array(rptnames)[on_limiter]
    zspt = np.array(zptnames)[on_limiter]

    # Load to ODS
    for i in range(len(rbpt)):
        bry[i]['r.reference_type'] = bry[i]['z.reference_type'] = 1
        bry[i]['r.reference_name'] = rbpt[i]
        bry[i]['z.reference_name'] = zbpt[i]
        bry[i]['r.reference.time'] = bry[i]['z.reference.time'] = t * 1e-3
        bry[i]['r.reference.data'] = rbdry[:, i]
        bry[i]['z.reference.data'] = zbdry[:, i]

    for i in range(2):
        xpt[i]['r.reference_type'] = xpt[i]['z.reference_type'] = 1
        xpt[i]['r.reference_name'] = xpt[i]['z.reference_name'] = ['Lower X-point', 'Upper X-point'][i]
        xpt[i]['r.reference.time'] = xpt[i]['z.reference.time'] = t * 1e-3
        xpt[i]['r.reference.data'] = rx[:, i]
        xpt[i]['z.reference.data'] = zx[:, i]

    for i in range(len(rspt)):
        # Find any other strike points that have the same sign of Z
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value.*')
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='Mean of empty slice')
            buddy = [j for j in range(len(rspt)) if (j != i) and ((np.nanmean(zstrk[:, j]) > 0) == (np.nanmean(zstrk[:, i]) > 0))]
            istop = np.nanmean(zstrk[:, i]) > 0
            if len(buddy) == 1:
                # One other strike point with same sign of Z: compare to it
                isouter = np.nanmean(rstrk[:, i]) > np.nanmean(rstrk[:, buddy[0]])
            else:
                # No other strike points or too many other strike points with same sign of Z: compare to X-point instead
                isouter = np.nanmean(rstrk[:, i]) > np.nanmean(rx[:, int(istop)])

            if ~np.isnan(istop) & ~np.isnan(isouter):
                this_valid = valid_strikes[2 * istop + isouter][keep_sample]
                rstrk[~this_valid, i] = np.NaN
                zstrk[~this_valid, i] = np.NaN
                if debug:
                    debug_out['this_strike_valid_{}'.format(i)] = this_valid
        stk[i]['r.reference_type'] = stk[i]['z.reference_type'] = 1
        stk[i]['r.reference.time'] = stk[i]['z.reference.time'] = t * 1e-3
        stk[i]['r.reference_name'] = rspt[i]
        stk[i]['z.reference_name'] = zspt[i]
        stk[i]['r.reference.data'] = rstrk[:, i]
        stk[i]['z.reference.data'] = zstrk[:, i]

    if debug:
        debug_out['rstrike'] = rstrk
        debug_out['zstrike'] = zstrk
        debug_out['keep_sample'] = keep_sample

    return {}


def setup_pulse_schedule_hardware_description_general(ods, pulse, device=None):
    """
    Sets up the pulse_schedule ODS, which holds control information

    This is a pretty broad category! Not all subsets are supported so far. Sorry.

    :param ods: ODS instance
    :param pulse: int
    :param device: string
    :return: dict
        Information or instructions for follow up in central hardware description setup
    """

    def update_instructions(ins, new_ins):
        if 'postcommands' in new_ins:
            if 'postcommands' in ins:
                ins['postcommands'] += new_ins['postcommands']
            else:
                ins['postcommands'] = new_ins['postcommands']

    instructions = {}
    update_instructions(instructions, setup_position_control_hardware_description_general(ods, pulse, device=device))

    return instructions


def pf_coils_to_ods(ods, coil_data):
    """
    Transfers poloidal field coil geometry data from a standard format used by efitviewer to ODS.

    WARNING: only rudimentary identifies are assigned.
    You should assign your own identifiers and only rely on this function to assign numerical geometry data.

    :param ods: ODS instance
        Data will be added in-place
    :param coil_data: 2d array
        coil_data[i] corresponds to coil i. The columns are R (m), Z (m), dR (m), dZ (m), tilt1 (deg), and tilt2 (deg)
        This should work if you just copy data from iris:/fusion/usc/src/idl/efitview/diagnoses/<device>/*coils*.dat
        (the filenames for the coils vary)
    :return: ODS instance
    """

    from omas.omas_plot import geo_type_lookup

    rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
    outline_code = geo_type_lookup('outline', 'pf_active', ods.imas_version, reverse=True)

    nc = len(coil_data[:, 0])

    for i in range(nc):
        ods['pf_active.coil'][i]['name'] = ods['pf_active.coil'][i]['identifier'] = 'PF{}'.format(i)
        if (coil_data[i, 4] == 0) and (coil_data[i, 5] == 0):
            rect = ods['pf_active.coil'][i]['element.0.geometry.rectangle']
            rect['r'] = coil_data[i, 0]
            rect['z'] = coil_data[i, 1]
            rect['width'] = coil_data[i, 2]  # Or width in R
            rect['height'] = coil_data[i, 3]  # Or height in Z
            ods['pf_active.coil'][i]['element.0.geometry.geometry_type'] = rect_code
        else:
            outline = ods['pf_active.coil'][i]['element.0.geometry.outline']
            fdat = coil_data[i]
            fdat[4] = -coil_data[i, 4] * np.pi / 180.0
            fdat[5] = -(coil_data[i, 5] * np.pi / 180.0 if coil_data[i, 5] != 0 else np.pi / 2)
            outline['r'] = [
                fdat[0] - fdat[2] / 2.0 - fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                fdat[0] - fdat[2] / 2.0 + fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                fdat[0] + fdat[2] / 2.0 + fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                fdat[0] + fdat[2] / 2.0 - fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
            ]
            outline['z'] = [
                fdat[1] - fdat[3] / 2.0 - fdat[2] / 2.0 * np.tan(-fdat[4]),
                fdat[1] + fdat[3] / 2.0 - fdat[2] / 2.0 * np.tan(-fdat[4]),
                fdat[1] + fdat[3] / 2.0 + fdat[2] / 2.0 * np.tan(-fdat[4]),
                fdat[1] - fdat[3] / 2.0 + fdat[2] / 2.0 * np.tan(-fdat[4]),
            ]
            ods['pf_active.coil'][i]['element.0.geometry.geometry_type'] = outline_code

    return ods


def toray_to_omas(ech_nml, uf_azi, uf_pol, uf_pow, ods=None, root=None):
    """
    Given 3 ECH UFILEs (azimuthal angle, polar angle, and power), return an ODS with the launcher info filled out

    :param ech_nml: A TORAY namelist

    :param uf_azi: An ECH Ufile containing the azimuthal angle

    :param uf_pol: An ECH Ufile containing the polar angle

    :param uf_pow: An ECH Ufile containing the power

    :param ods: An existing ODS, to which to add the launcher info from the Ufiles

    :param root: An OMFITmodule instance (for experiment and generic OMFIT info)
    """
    if ods is None:
        ods = ODS()
    t_in = ech_nml
    ec = ods['ec_launchers']
    if root is not None:
        add_experiment_info_to_ods(ods, root=root)
        add_generic_OMFIT_info_to_ods(ods, root=root)
    ids_prop = ec['ids_properties']
    ids_prop['comment'] = 'ECH data from Ufile input in OMFIT'
    ids_prop['source'] = ids_prop['comment']
    ids_prop['homogeneous_time'] = True
    ids_prop['provider'] = os.environ['USER']
    ids_prop['creation_date'] = time.ctime()
    ec['time'] = uf_pow['X0']['data']

    numb = int(t_in['NANTECH'])
    myphi = float(t_in['PHECECH']) * np.pi / 180.0  # toroidal position of the source in [deg]. Useless for axi-symetric plasma

    for i in range(numb):
        length = len(uf_azi['F']['data'][:, i])
        myfreq = t_in['FREQECH'][i]
        antenna = ec['launcher.%d' % i]
        antenna['frequency.data'] = [myfreq] * length

        antenna['steering_angle_pol.data'] = (uf_pol['F']['data'][:, i] - 90.0) * np.pi / 180.0  # polar angle from ECA UFILE in [deg]
        antenna['steering_angle_tor.data'] = (uf_azi['F']['data'][:, i] - 180.0) * np.pi / 180.0  # Azimutal angle from ECB UFILE in [deg]
        antenna['name'] = 'EC%d' % (i + 2)  # arbitrary name
        antenna['identifier'] = 'EC%d' % (i + 2)  # arbitrary identifier
        antenna['power_launched.data'] = uf_pow['F']['data'][:, i]  # power en W, from ECP UFILE
        myr = float(t_in['XECECH'][i]) / 100.0  # R position of the source from TRANSP input in [cm]
        myz = float(t_in['ZECECH'][i]) / 100.0  # Z position of the source from TRANSP input in [cm]
        antenna['launching_position.r'] = [myr] * length
        antenna['launching_position.z'] = [myz] * length
        antenna['launching_position.phi'] = [myphi] * length

    return ods


def nubeam_to_omas(nb_nml, nb_uf=None, ods=None, root=None):
    """
    Given a NUBEAM namelist and UFILE, return an ODS with the beam info filled out

    :param nb_nml: A NUBEAM namelist

    :param nb_uf: A NUBEAM Ufile

    :param ods: An existing ODS, to which to add the beam info from the namelist and Ufile

    :param root: An OMFITmodule instance (for experiment and generic OMFIT info)
    """
    import pint

    ureg = pint.UnitRegistry()
    cm = ureg('cm')
    deg = ureg('deg')
    meter = ureg('m')

    if ods is None:
        ods = ODS()
    t_in = nb_nml
    nbi = ods['nbi']

    if root is not None:
        add_experiment_info_to_ods(ods, root=root)
        add_generic_OMFIT_info_to_ods(ods, root=root)
    ids_prop = nbi['ids_properties']
    ids_prop['comment'] = 'NBI data produced from NUBEAM namelist and Ufile input in OMFIT'
    ids_prop['source'] = ids_prop['comment']
    ids_prop['homogeneous_time'] = True
    ids_prop['provider'] = os.environ['USER']
    ids_prop['creation_date'] = time.ctime()
    if nb_uf is not None:
        nbi['time'] = nb_uf['X0']['data']
        if 'BEAMS' in nb_uf:
            numb = len(nb_uf['BEAMS'])
            beams = nb_uf['BEAMS']
        else:
            numb = int(nb_uf['SCALARS'][0]['data'])
            beams = ['beam_%d' % i for i in range(numb)]
    else:
        nbi['time'] = [0]
        numb = len(nb_nml['PINJA'])
        beams = ['beam_%d' % i for i in range(numb)]

    def get_arr_var(avar, ind):
        """
        A convenience function to do

        return t_in[avar][ind] if avar in t_in else t_in[avar[:-1]]
        """
        if not avar.endswith('A'):
            raise ValueError('The variable requested, %s, does not end with A, and is probably an error' % avar)
        return t_in[avar][ind] if avar in t_in else t_in[avar[:-1]]

    for bi, beam in enumerate(beams):
        unit = nbi['unit.%d' % bi]
        unit['name'] = beam
        unit['identifier'] = beam
        unit['species.a'] = get_arr_var('ABEAMA', bi)
        unit['species.z_n'] = get_arr_var('XZBEAMA', bi)
        if nb_uf is not None:
            cf = unit['beam_current_fraction.data'] = np.array(
                [
                    nb_uf['F']['data'][:, numb * 2 + bi],
                    nb_uf['F']['data'][:, numb * 3 + bi],
                    [
                        0 if a == 0 and b == 0 else 1 - a - b
                        for a, b in zip(nb_uf['F']['data'][:, numb * 2 + bi], nb_uf['F']['data'][:, numb * 3 + bi])
                    ],
                ]
            )
        else:
            ffulla = get_arr_var('FFULLA', bi)
            fhalfa = get_arr_var('FHALFA', bi)
            unit['beam_current_fraction.data'] = cf = [[ffulla], [fhalfa], [1 - ffulla - fhalfa]]
        # unit['beam_current_fraction.time'] = homogeneous time
        tmp = cf / (np.array([1.0, 2.0, 3.0])[:, np.newaxis])
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value encountered in true_divide')
            stmp = np.sum(tmp, axis=0)
            stmp[stmp == 0.0] = 1.0
            unit['beam_power_fraction.data'] = tmp / stmp
        # unit['beam_power_fraction.time'] = homogeneous time
        if nb_uf is not None:
            unit['energy.data'] = nb_uf['F']['data'][:, numb + bi]  # NUBEAM already in eV
            # unit['energy.time'] = homogeneous time
            unit['power_launched.data'] = nb_uf['F']['data'][:, bi]
        else:
            unit['power_launched.data'] = [get_arr_var('PINJA', bi)]
            unit['energy.data'] = [get_arr_var('EINJA', bi)]

        # unit['power_launched.time'] = homogeneous time
        bg = unit['beamlets_group.0']
        angv = bg['angle'] = -np.arcsin((get_arr_var('XYBSCA', bi) - get_arr_var('XYBAPA', bi)) / get_arr_var('XLBAPA', bi))
        bg['position.z'] = get_arr_var('XYBSCA', bi) * cm
        bg['position.r'] = np.sqrt(get_arr_var('XLBTNA', bi) ** 2 * np.cos(angv) + get_arr_var('RTCENA', bi) ** 2) * cm
        # bg['position.phi'] - Toroidal angle (oriented counter-clockwise when viewing from above)
        # XBZETA(IB)= toroidal angle of the beam source in an (R,zeta,Z)
        #            right handed coordinate system (deg).
        bg['position.phi'] = -get_arr_var('XBZETA', bi) * deg
        # bg['direction'] - Direction of the beam seen from above the torus:
        #                     -1 = clockwise; 1 = counter clockwise
        # NLCO - .TRUE. if the beam is CO-injecting with the plasma current.
        # NLJCCW - .TRUE.  ! orientation of Ip (.TRUE. for counter-clockwise)
        #                 Here "counter-clockwise" is as seen looking down on the tokamak from above.
        bg['direction'] = (2 * int(t_in['NLJCCW']) - 1) * (2 * int(t_in['NLCO'][bi]) - 1)
        bg['tangency_radius'] = get_arr_var('RTCENA', bi) * cm
        bg['focus.focal_length_horizontal'] = get_arr_var('FOCLRA', bi) * cm
        bg['focus.focal_length_vertical'] = get_arr_var('FOCLZA', bi) * cm
        dc = bg['divergence_component.0']
        dc['particles_fraction'] = 1.0
        dc['vertical'] = get_arr_var('DIVZA', bi)
        dc['horizontal'] = get_arr_var('DIVRA', bi)
        shape = get_arr_var('NBSHAPA', bi)
        if shape == 1:
            bg['width_horizontal'] = get_arr_var('BMWIDRA', bi) * 2 * cm
            bg['width_vertical'] = get_arr_var('BMWIDZA', bi) * 2 * cm
        else:
            raise NotImplementedError('IMAS only has rectangular sources')

        R = bg['position.r'] * meter  # Radius of source
        PHI = bg['position.phi']  # Angle of source
        XLBAPA = get_arr_var('XLBAPA', bi) * cm
        XYBAPA = get_arr_var('XYBAPA', bi) * cm
        RTCENA = get_arr_var('RTCENA', bi) * cm
        XLBTNA = get_arr_var('XLBTNA', bi) * cm
        aperture = unit['aperture.0.centre']

        # SPS 19 Dec 2019
        # Verified that the following maintained constant radial aperture
        # (of value less than R, and satifying law of cosines)
        # while PHI rotated through 2pi

        # Right triangle with legs XLBTNA and RTCENA, angb opposite RTCENA
        angb = np.arctan2(RTCENA, XLBTNA) * bg['direction']
        # Law of cosines
        # aperture['r'] = sqrt(R**2 + (XLBAPA * cos(angv))**2 - 2 * R * XLBAPA * cos(angv) * cos(angb))
        x_disp_from_source = XLBAPA * np.cos(angv) * np.cos(PHI - np.pi + angb)
        y_disp_from_source = XLBAPA * np.cos(angv) * np.sin(PHI - np.pi + angb)
        x_source = R * np.cos(PHI)
        y_source = R * np.sin(PHI)
        x_ap = x_source + x_disp_from_source
        y_ap = y_source + y_disp_from_source
        aperture['r'] = (np.sqrt(x_ap ** 2 + y_ap ** 2)).to(meter).magnitude
        aperture['phi'] = (np.arctan2(y_ap, x_ap)).to(ureg.radian).magnitude
        aperture['z'] = XYBAPA.to(meter).magnitude

        '''
        nbi%unit(:)%beamlets_group(:)%beamlets%tangency_radii(:)    machine
        nbi%unit(:)%beamlets_group(:)%beamlets%angles(:)    machine
        nbi%unit(:)%beamlets_group(:)%beamlets%power_fractions(:)    machine
        nbi%unit(:)%beamlets_group(:)%beamlets%positions%r(:)    machine
        nbi%unit(:)%beamlets_group(:)%beamlets%positions%z(:)    machine
        nbi%unit(:)%beamlets_group(:)%beamlets%positions%phi(:)    machine
        '''
    return ods


def transp_ic_to_omas(tr_in, ods=None, uf_p=None, uf_f=None, root=None):
    """
    Convert the TRANSP input namelist, tr_in, to omas

    :param tr_in: A TRANSP input namelist (TR.DAT)

    :param ods: An existing ODS object to update with IC antenna/power info

    :param uf_p: A ufile with power traces

    :param uf_f: A ufile with frequency traces

    :param root: An OMFITmodule instance (for experiment and generic OMFIT info)
    """
    import pint

    ureg = pint.UnitRegistry()
    cm = ureg('cm')
    deg = ureg('deg')
    if ods is None:
        ods = ODS()
    if root is not None:
        add_experiment_info_to_ods(ods, root=root)
        add_generic_OMFIT_info_to_ods(ods, root=root)
    ic = ods['ic_antennas']
    ids_prop = ic['ids_properties']
    ids_prop['comment'] = 'ICRF data produced from TRANSP namelist and Ufile input in OMFIT'
    ids_prop['source'] = ids_prop['comment']
    ids_prop['homogeneous_time'] = False
    ids_prop['provider'] = os.environ['USER']
    ids_prop['creation_date'] = time.ctime()

    tr_in = tr_in.flatten()
    na = tr_in['NICHA']

    def get_arr_var(avar, ind):
        """
        A convenience function to do

        return tr_in[avar][ind] if avar in tr_in else tr_in[avar[:-1]]
        """
        if not avar.endswith('A'):
            raise ValueError('The variable requested, %s, does not end with A, and is probably an error' % avar)
        return tr_in[avar][ind] if avar in tr_in else tr_in[avar[:-1]]

    for ai in range(na):
        ant = ic['antenna.%s' % ai]
        mod = ant['module.0']
        mod['name'] = ant['name'] = str(ai)
        mod['identifier'] = ant['identifier'] = str(ai)
        if uf_f is None:
            ton = get_arr_var('TONICHA', ai)
            toff = get_arr_var('TOFFICHA', ai)
            dt = 0.1 * (toff - ton)
            mod['frequency.time'] = ant['frequency.:.time'] = [ton - dt, ton - dt / 1e3, ton, toff, toff + dt / 1e3, toff + dt]
            freq = get_arr_var('FRQICHA', ai)
            mod['frequency.data'] = ant['frequency.:.data'] = [0, 0, freq, freq, 0, 0]
        else:
            mod['frequency.time'] = ant['frequency.time'] = uf_f['X0']['data']
            mod['frequency.data'] = ant['frequency.data'] = uf_f['F']['data'][:, ai]
        if uf_p is None:
            ton = get_arr_var('TONICHA', ai)
            toff = get_arr_var('TOFFICHA', ai)
            dt = 0.1 * (toff - ton)
            power = get_arr_var('PRFICHA', ai)
            mod['power_launched.time'] = ant['power_launched.time'] = [ton - dt, ton - dt / 1e3, ton, toff, toff + dt / 1e3, toff + dt]
            mod['power_launched.data'] = ant['power_launched.data'] = [0, 0, power, power, 0, 0]
        else:
            mod['power_launched.time'] = ant['power_launched.time'] = uf_p['X0']['data']
            mod['power_launched.data'] = ant['power_launched.data'] = uf_p['F']['data'][:, ai]
            # ant['power_launched.data'] = uf_p # Need real ufile to fill this in
        strap = mod['strap.0']
        rant = tr_in['RGEOANT_A'][:, ai]
        zant = tr_in['YGEOANT_A'][:, ai]
        ind = ~np.isnan(rant) & ~np.isnan(zant)
        r = strap['outline.r'] = rant[ind] * cm
        strap['outline.z'] = zant[ind] * cm
        strap['outline.phi'] = [0] * len(r)  # Not in the TRANSP input namelist...
        strap['distance_to_conductor'] = tr_in['RFARTR_A'][ai] * cm
        if root and is_device(root['SETTINGS']['EXPERIMENT']['device'], 'JET'):
            phase = 0
            nphi = tr_in['NNPHI'][1, ai + 1]
            if nphi == 27:
                phase = ([-np.pi / 2.0, np.pi / 2] * 2 + [0])[ai]
            else:
                print('tr_in["NNPHI"]=', tr_in['NNPHI'])
                raise NotImplementedError('Spectrum %s not yet adapted' % nphi)
            mod['phase_forward.time'] = mod['power_launched.time']
            mod['phase_forward.data'] = [phase] * len(mod['phase_forward.time'])
    ic['time'] = [tr_in['TINIT'], tr_in['FTIME']]  # Not used, but filled with total TRANSP time
    return ods

    # Missing
    # ic_antennas%antenna(:)%module(:)%phase%data(:)
    # ic_antennas%antenna(:)%module(:)%phase%time(:)
    # ic_antennas%antenna(:)%module(:)%strap(:)%outline%phi    machine
    # ic_antennas%antenna(:)%module(:)%strap(:)%width_tor    machine
    # ic_antennas%code    optional
    # ic_antennas%reference_point%r    optional
    # ic_antennas%reference_point%z    optional


def make_sample_ods(device='test', shot=123456, efitid='fakesample'):
    """
    Generates an ODS with some minimal test data, including a sample equilibrium and at least one hardware system
    :param device: string
    :param shot: int
    :param efitid: string
    :return: ODS
    """
    ods = ODS()
    ods.sample_equilibrium()
    ods.sample_gas_injection()
    ods['dataset_description.data_entry']['machine'] = device
    ods['dataset_description.data_entry']['pulse'] = shot
    ods['dataset_description.ids_properties.comment'] = 'Test data; EFIT tree = {}'.format(efitid)
    return ods


def orthogonal_distance(ods, r0, z0, grid=True, time_range=None, zf=5, maxstep=5e-4, minstep=1e-5, maxsteps=5000, debug=False):
    """
    Calculates the orthogonal distance from some point(s) to the LCFS

    Works by stepping along the steepest gradient until the LCFS is reached.

    :param ods: ODS instance
        A complete, top level ODS, or selection of time slices from equilibrium.
        That is, `ods['equilibrium']['time_slice']`, if `ods` is a top level ODS.

    :param r0: 1D float array
        R coordinates of the point(s) in meters.
        If grid=False, the arrays must have length matching the number of time slices in equilibrium.

    :param z0: 1D float array
        Z coordinates of the point(s) in meters.
        Length must match r0

    :param grid: bool
        Return coordinates on a time-space grid, assuming each point in R-Z is static and given a separate history.
        Otherwise (grid=False), assume one point is given & it moves in time, so return array will be 1D vs. time.

    :param time_range: 2 element numeric iterable [optional]
        Time range in seconds to use for filtering time_slice in ODS

    :param zf: float
        Zoom factor for upsampling the equilibrium first to improve accuracy. Ignored unless > 1.

    :param maxstep: float
        Maximum step size in m
        Restraining step size should prevent flying off the true path

    :param minstep: float
        Minimum step size in m
        Prevent calculation from taking too long by forcing a minimum step size

    :param maxsteps: int
        Maximum number of steps allowed in path tracing. Protection against getting stuck in a loop.

    :param debug: bool
        Returns a dictionary with internal quantities instead of an array with the final answer.

    :return: float array
        Length of a path orthogonal to flux surfaces from (r0, z0) to LCFS, in meters.
        If grid=True: 2D float array (time by points)
        If grid=False: a 1D float array vs. time
    """

    # Auto select timing
    eqt = ods['.equilibrium.time']
    if time_range is None:
        time_slices = range(len(eqt))
    else:
        time_slices = where((eqt >= time_range[0]) & (eqt <= time_range[1]))[0]

    # Sanitize/check inputs
    def check_input(condition, message=None):
        if not condition:
            raise OmasUtilsBadInput(message)

    r0 = np.atleast_1d(r0)
    z0 = np.atleast_1d(z0)
    check_input(len(r0) == len(z0), 'R (len={len(r0)}) and Z (len={len(z0)}) arrays must have the same length.')
    if not grid:
        check_input(len(r0) == len(time_slices), 'R (len={len(r0)}) must have same # of elements as time-slices.')

    # Prepare to catch output
    if grid:
        results = np.empty((len(time_slices), len(r0)))
        paths = [[None] * len(r0)] * len(time_slices)
    else:
        results = np.empty(len(time_slices))
        paths = [None] * len(time_slices)
    results[:] = np.NaN

    # Process each time slice separately
    for i, time_slice in enumerate(time_slices):
        # Extract basic data
        eq = ods['.equilibrium.time_slice'][time_slice]
        psib = eq['global_quantities.psi_boundary']
        psia = eq['global_quantities.psi_axis']
        psi_ = eq['profiles_2d.0.psi']
        rgrid_ = eq['profiles_2d.0.grid.dim1']
        zgrid_ = eq['profiles_2d.0.grid.dim2']

        # Optional upsample to improve accuracy
        if zf > 1:
            psi = scipy.ndimage.zoom(psi_, zf)
            rgrid = scipy.ndimage.zoom(rgrid_, zf)
            zgrid = scipy.ndimage.zoom(zgrid_, zf)
        else:
            psi = psi_
            rgrid = rgrid_
            zgrid = zgrid_

        # Gradients and interpolation
        psin = (psi - psia) / (psib - psia)
        dpsi = np.gradient(psin)
        dpsidr = dpsi[0] / np.gradient(rgrid)
        dpsidz = dpsi[1] / np.gradient(zgrid)
        dri = interp2d(rgrid, zgrid, dpsidr.T)
        dzi = interp2d(rgrid, zgrid, dpsidz.T)
        psini = interp2d(rgrid, zgrid, psin.T)

        # Pick which points to consider for this time-slice
        if grid:
            eligible_r0 = r0
            eligible_z0 = z0
        else:
            eligible_r0 = np.atleast_1d(r0[i])
            eligible_z0 = np.atleast_1d(z0[i])

        # Process each point individually
        for j in range(len(eligible_r0)):
            # Prepare to step along the path of steepest gradient
            pathr = [eligible_r0[j]]
            pathz = [eligible_z0[j]]
            r = eligible_r0[j]
            z = eligible_z0[j]
            psin0 = psini(eligible_r0[j], eligible_z0[j])
            signdir = -1 if psin0 > 1 else 1

            # Step along the path
            for m in range(maxsteps):
                # Pick default step and direction
                rstep = signdir * dri(r, z)
                zstep = signdir * dzi(r, z)
                steplen = np.sqrt(rstep ** 2 + zstep ** 2)
                stepdir = np.arctan2(zstep, rstep)[0]
                # Apply stepsize limits
                if steplen > maxstep:
                    steplen = maxstep
                if steplen < minstep:
                    steplen = minstep
                # Take the step
                rstep = np.cos(stepdir) * steplen
                zstep = np.sin(stepdir) * steplen
                r += rstep
                z += zstep
                pathr += [r]
                pathz += [z]
                # Check to see if the LCFS has been reached
                if (psini(r, z) < 1) and (psin0 > 1):
                    break
                elif (psini(r, z) > 1) and (psin0 < 1):
                    break
            else:
                # Ran out of steps before reaching the LCFS
                printw(
                    f"Didn't finish tracing back to LCFS: time-slice#{i} ({time_slice}), point#{j} "
                    f"({eligible_r0[j], eligible_z0[j]}); stopped after {m} steps."
                )
                if grid:
                    results[i, j] = np.NaN
                else:
                    results[i] = np.NaN

            # Measure path length
            pathdr = np.array(np.diff(pathr))
            pathdz = np.array(np.diff(pathz))
            pathds = np.sqrt(pathdr ** 2 + pathdz ** 2)
            if grid:
                results[i, j] = np.sum(pathds)
                paths[i][j] = (pathr, pathz)
            else:
                results[i] = np.sum(pathds)
                paths[i] = (pathr, pathz)

    if debug:
        return dict(results=results, paths=paths)
    return results


def load_sample_eq_specifications(ods, hrts_gate='any'):
    """
    Loads a sample of equilibrium shape specifications under pulse_schedule

    :param ods: ODS instance
        Data go here

    :param hrts_gate: str
        One of the boundary points is for checking whether the boundary passes through the HRTS range.
        But DIII-D's HRTS can be reconfigured to handle three different ranges! So you can select
        'top': Relevant when the HRTS channels are positioned high (this might be the default position)
        'mid'
        'low'
        'any': goes from the bottom of the 'low' range to the top of the 'top' range.
    """
    pc = ods['pulse_schedule.position_control']

    ref_type = 1  # 1 is absolute, 0 is relative. Not sure what that means, but 1 seems more likely to be relevant.
    timing = [0, 10]  # Central time range to cover a typical DIII-D shot
    nt = len(timing)

    # "Boundary" points that are actually on the divertor leg in the example (no where else to put them yet)
    pc['boundary_outline'][0]['r.reference_type'] = ref_type
    pc['boundary_outline'][0]['r.reference_name'] = 'outer div leg angle enforcer'
    pc['boundary_outline'][0]['r.reference.time'] = timing
    pc['boundary_outline'][0]['r.reference.data'] = [ufloat(1.4966, 0.001)] * nt
    pc['boundary_outline'][0]['z'] = copy.deepcopy(pc['boundary_outline'][0]['r'])
    pc['boundary_outline'][0]['z.reference.data'] = [ufloat(1.2293, 0.001)] * nt

    # X points
    pc['x_point'][0]['r.reference_name'] = 'primary'
    pc['x_point'][0]['r.reference_type'] = ref_type
    pc['x_point'][0]['r.reference.time'] = timing
    pc['x_point'][0]['r.reference.data'] = [ufloat(1.338, 0.02)] * nt
    pc['x_point'][0]['z'] = copy.deepcopy(pc['x_point'][0]['r'])
    pc['x_point'][0]['z.reference.data'] = [ufloat(1.019, 0.02)] * nt

    # Strike points
    pc['strike_point'][0]['r.reference_name'] = 'outer primary'
    pc['strike_point'][0]['r.reference_type'] = ref_type
    pc['strike_point'][0]['r.reference.time'] = timing
    pc['strike_point'][0]['r.reference.data'] = [ufloat(1.503, 0.001)] * nt
    pc['strike_point'][0]['z'] = copy.deepcopy(pc['strike_point'][0]['r'])
    pc['strike_point'][0]['z.reference.data'] = [ufloat(1.237, 0.001)] * nt

    pc['strike_point'][1]['r'] = copy.deepcopy(pc['strike_point'][0]['r'])
    pc['strike_point'][1]['r.reference_name'] = 'inner primary'
    pc['strike_point'][1]['r.reference.data'] = [ufloat(1.016, 0.2)] * nt
    pc['strike_point'][1]['z'] = copy.deepcopy(pc['strike_point'][1]['r'])
    pc['strike_point'][1]['z.reference.data'] = [ufloat(1.109, 0.2)] * nt

    # Gates
    pc['flux_gates'][0]['name'] = 'slot entrance'
    pc['flux_gates'][0]['r1'] = 1.486
    pc['flux_gates'][0]['r2'] = 1.404
    pc['flux_gates'][0]['z1'] = 1.117
    pc['flux_gates'][0]['z2'] = 1.157
    pc['flux_gates'][0]['applies_to_psin'] = 1.0
    pc['flux_gates'][0]['applies_to_dr_mid'] = 0.005

    i = 1
    hrts_gates = dict(top=[0.65, 0.74], mid=[0.57, 0.73], low=[0.47, 0.67])
    hrts_gates['any'] = [hrts_gates['low'][0], hrts_gates['top'][1]]
    hrts_zrange = hrts_gates[hrts_gate]
    pc['flux_gates'][i]['name'] = f'HRTS gate {hrts_gate}'
    pc['flux_gates'][i]['r1'] = 1.94
    pc['flux_gates'][i]['r2'] = 1.94
    pc['flux_gates'][i]['z1'] = hrts_zrange[0]
    pc['flux_gates'][i]['z2'] = hrts_zrange[1]
    pc['flux_gates'][i]['time_range'] = [1.5, 4.9]


def omas_eq1d_pretty_name(quantity, include_units=True):
    """
    Translates ODS tag names into pretty names that are suitable for use in plot axes labels

    :param quantity: str
        Key within equilibrium.time_slice.:.profiles_1d

    :param include_units: bool
        Include units in the return string

    :return: str
    """
    if quantity == 'psi_norm':
        label = r'$\psi_N$'
        units = ''
    elif quantity == 'dpressure_dpsi':
        label = r'$d_{\psi} p$'
        units = 'Pa Wb$^{-1}$'
    elif quantity == 'f_df_dpsi':
        label = r'$F d_{\psi} F$'
        units = 'T$^2$ m$^2$ Wb$^{-1}$'
    elif quantity == 'rho_tor_norm':
        label = r'$\rho_N$'
        units = ''
    elif quantity == 'r_outboard':
        label = '$R_{OMP}$'
        units = 'm'
    elif quantity == 'r_inboard':
        label = '$R_{IMP}$'
        units = 'm'
    else:
        info = omas_info_node(f'equilibrium.time_slice.:.profiles_1d.{quantity}')
        label = info.get('documentation', quantity).split('(')[0]
        if 'w.r.t.' in label:
            label = label.replace('w.r.t.', 'WwRrTt')
            label = label.split('.')[0]
            label = label.replace('WwRrTt', 'w.r.t.')
        else:
            label = label.split('.')[0]
        units = info.get('units', '')
    if units == '-':
        units = ''
    if units and include_units:
        label += f' / {units}'
    return label


class GradeEquilibrium:
    """
    Grade's an equilibrium shape's conformity to specified shape references
    """

    def __init__(self, ods, debug_out=None):
        """
        :param ods: ODS instance

        :param debug_out: dict-like [optional]
            Provide a place to store debugging output, or provide None to disable
        """
        self.ods = ods
        self.results = dict()
        self.debug_out = debug_out
        self.zoomed_eq_results = dict()
        self.hires_contour_results = dict()
        self.units = 'm'  # Units for spatial coordinates TODO read from OMAS instead of assuming

        self.fatline = rcParams['lines.linewidth'] * 1.25 + 1.25
        self.bigmark = 25
        self.bad_style = {'fontstyle': 'italic', 'fontweight': 'bold'}
        self.bad_alpha = 0.2

        try:
            from skimage import measure
        except Exception:
            self.have_skimage = False
        else:
            self.have_skimage = True

        self.grade()

    def printdq(self, *args, **kw):
        kw.setdefault('topic', 'GradeEquilibrium')
        printd(*args, **kw)

    def zoomed_eq(self, slice_index=0, zoom=7):
        """
        Returns an upsampled equilibrium, as may be needed for some methods

        :param slice_index: int
            Index of the time slice of the equilibrium
        :param zoom:
            zoom / upscaling factor
        :return: tuple
            1D float array: r values of the grid
            1D float array: z values of the grid
            2D float array: psi_N at (r, z)
        """
        tag = f'{slice_index}_{zoom:0.3f}'
        if tag in self.zoomed_eq_results:
            return self.zoomed_eq_results[tag]
        eq = self.ods['equilibrium']['time_slice'][slice_index]
        psia = eq['global_quantities']['psi_axis']
        psib = eq['global_quantities']['psi_boundary']
        psi = eq['profiles_2d'][0]['psi']
        r = eq['profiles_2d'][0]['grid']['dim1']
        z = eq['profiles_2d'][0]['grid']['dim2']
        psin = (psi - psia) / (psib - psia)
        rzoom = scipy.ndimage.zoom(r, zoom)
        zzoom = scipy.ndimage.zoom(z, zoom)
        psinzoom = scipy.ndimage.zoom(psin, zoom)
        self.zoomed_eq_results[tag] = (rzoom, zzoom, psinzoom)
        return rzoom, zzoom, psinzoom

    def hires_contour_sk(self, slice_index=0, psin=1, zoom=10):
        """
        Returns r, z points along a high resolution contour at some psi_N value

        Requires skimage package, which isn't required by OMFIT and may not be available.
        THIS IS BETTER IF IT IS AVAILABLE!

        :param slice_index: int
            Index of the time slice of the equilibrium
        :param psin: float
            psi_N of the desired contour
        :param zoom: float
            zoom / upscaling factor
        :return: list
            Each element is a section of the contour, which might not be connected (e.g. different curve for PFR)
            Each element is a 2D array, where [:, 0] is R and [:, 1] is Z
        """
        from skimage import measure

        r, z, psinmap = self.zoomed_eq(slice_index=slice_index, zoom=zoom)
        ridx = np.arange(len(r))
        zidx = np.arange(len(z))
        contours_raw = measure.find_contours(psinmap, psin)
        contours_rz = [array([interp1d(ridx, r)(cr[:, 0]), interp1d(zidx, z)(cr[:, 1])]).T for cr in contours_raw]
        return contours_rz

    def hires_contour_omf(self, slice_index=0, psin=1, zoom=10):
        """
        Returns r, z points along a high resolution contour at some psi_N value

        Uses OMFIT util functions. 10-50% slower than skimage, but doesn't require external dependencies.
        skimage is better if you have it!

        :param slice_index: int
            Index of the time slice of the equilibrium
        :param psin: float
            psi_N of the desired contour
        :param zoom: float
            zoom / upscaling factor
        :return: list
            Each element is a section of the contour, which might not be connected (e.g. different curve for PFR)
            Each element is a 2D array, where [:, 0] is R and [:, 1] is Z
        """
        r, z, psinmap = self.zoomed_eq(slice_index=slice_index, zoom=zoom)
        contours_rz = contourPaths(r, z, psinmap.T, levels=np.atleast_1d(psin), smooth_factor=1)
        contours_rz = [crz.vertices for crz in contours_rz[0]]
        return contours_rz

    def hires_contour(self, slice_index=0, psin=1, zoom=10):
        """Wrapper for picking whether to use omfit or skimage version"""
        tag = f'{slice_index}_{zoom:0.3f}_{psin:0.3f}'
        if tag in self.hires_contour_results:
            return self.hires_contour_results[tag]
        if self.have_skimage:
            result = self.hires_contour_sk(slice_index=slice_index, zoom=zoom, psin=psin)
        else:
            result = self.hires_contour_omf(slice_index=slice_index, zoom=zoom, psin=psin)
        self.hires_contour_results[tag] = result
        return result

    def find_midplane(self, slice_index):
        """
        Finds the intersection of the boundary with the outboard midplane

        :param slice_index: int

        :return: (float, float)
            R, Z coordinates of the LCFS at the outboard midplane
        """
        rmaxis = self.ods['equilibrium']['time_slice'][slice_index]['global_quantities']['magnetic_axis']['r']
        zmaxis = self.ods['equilibrium']['time_slice'][slice_index]['global_quantities']['magnetic_axis']['z']
        contours = self.hires_contour(slice_index=slice_index, psin=1)
        # Find the contour section that crosses the midplane
        lowz = np.array([abs(contour[:, 1]).min(0) for contour in contours])
        contour = np.array(contours)[np.argmin(lowz)]
        sel = (contour[:, 0] > rmaxis) & ((abs(contour[:, 1] - zmaxis)) < 0.25)
        rmidout = interp1d(contour[sel, 1], contour[sel, 0])(zmaxis)
        return rmidout, zmaxis

    def find_fluxsurface(self, slice_index=0, midplane_dr=0.005):
        """
        Finds contour segments of a flux surface outboard of the midplane by a specific amount

        :param slice_index: int

        :param midplane_dr: float

        :return: list of 2D arrays
            Sections of the contour for the flux surface
            The contour may have some disconnected regions in general, but if it is all simply connected,
            there will be only one element in the list with a single 2D array.
        """
        rmidout, zmaxis = self.find_midplane(slice_index=slice_index)
        r, z, psin = self.zoomed_eq(slice_index=slice_index)
        psin_val = interp2d(r, z, psin.T)(rmidout + midplane_dr, zmaxis)[0]
        contours = self.hires_contour(slice_index=slice_index, psin=psin_val)
        return contours

    def new_fig(self, slice_index=0):
        """Prepares a new figure and set of axes with aspect ratio and cornernote set up"""
        fig, ax = plt.subplots(1)
        ax.set_aspect('equal')
        ax.set_adjustable('box')
        de = self.ods['dataset_description.data_entry']
        eq = self.ods['equilibrium.time_slice'][slice_index]
        cornernote(device=de.get('machine', ''), shot=de.get('pulse', ''), time=eq['time'] * 1000)
        return fig, ax

    def plot_hires_eq(self, slice_index=0, ax=None, psin=None, r_rsep=None, track=None, **plotkw):
        """
        Plots the high resolution contours generated for the grading process.

        Can be used with `track` to track whether a flux surface is already shown
        to avoid redundant overlays of the same thing.

        :param slice_index: int

        :param psin: float

        :param r_rsep: float

        :param ax: Axes instance

        :param track: dict-like [optional]
            Keeps track of what's already plotted to avoid redundant overlays of
            the same flux surfaces

        :param plotkw: extra keywords will be passed to plot
        """

        if track is not None and psin is not None and psin in track['p_contours_shown']:
            self.printdq(f'This contour at psin={psin} was already shown and will be skipped')
            return None

        if track is not None and r_rsep is not None and r_rsep in track['r_contours_shown']:
            self.printdq(f'This contour at R-Rsep={r_rsep} was already shown and will be skipped')
            return None

        if psin is not None:
            contours = self.hires_contour(slice_index=slice_index, psin=psin)
            track['p_contours_shown'] += [psin]
            plotkw.setdefault('label', rf'$\psi_N={psin:0.3f}$')
        elif r_rsep is not None:
            contours = self.find_fluxsurface(slice_index=slice_index, midplane_dr=r_rsep)
            track['r_contours_shown'] += [r_rsep]
            plotkw.setdefault('label', rf'$R-R_{{sep}}={r_rsep:0.3f}$ {self.units}')
        else:
            self.printdq('No contours specified; skipping plot')
            return None

        if ax is None:
            fig, ax = self.new_fig(slice_index=slice_index)

        plotkw.setdefault('color', 'b')

        for contour in contours:
            ax.plot(contour[:, 0], contour[:, 1], **plotkw)

        return ax

    def plot_flux_gates(self, slice_index=0, ax=None, track=None):
        """
        Plots locations of flux gates

        :param slice_index: int

        :param ax: Axes instance

        :param track: dict-like [optional]
        """
        if ax is None:
            fig, ax = self.new_fig(slice_index=slice_index)

        for fgi in self.ods['pulse_schedule.position_control.flux_gates']:
            g = self.ods['pulse_schedule.position_control.flux_gates'][fgi]
            name = g['name']
            rsurf = g.get('applies_to_dr_mid', [])
            psurf = g.get('applies_to_psin', [] if rsurf else 1)
            tr = g.get('time_range')
            eqt = self.ods['equilibrium.time_slice'][slice_index]['time']
            if (tr is not None) and (not (tr[0] <= eqt <= tr[1])):
                self.printdq(
                    f'Flux gate {name} applies to time range {tr} s; slice {slice_index} at {eqt} s is '
                    f'outside of this range. This gate will be skipped on the plot.'
                )
                continue

            lsurf1 = [rf'$\psi_N$={psurf}'] if len(np.atleast_1d(psurf)) else []
            lsurf2 = [rf'$R-R_{{sep}}$={rsurf} {self.units}'] if len(np.atleast_1d(rsurf)) else []
            lsurf = ', '.join(lsurf1 + lsurf2)

            # Make sure the relevant contours are shown
            cplot_kw = {'color': 'r', 'linestyle': '--', 'lw': 1}
            for p in np.atleast_1d(psurf):
                self.plot_hires_eq(slice_index=slice_index, ax=ax, track=track, psin=p, **cplot_kw)
            for r in np.atleast_1d(rsurf):
                self.plot_hires_eq(slice_index=slice_index, ax=ax, track=track, r_rsep=r, **cplot_kw)

            # Decide how well the gate was respected
            if 'flux_gates' in self.results:
                thru_gate = [v for k, v in self.results['flux_gates'][slice_index].items() if name in k]
                if len(thru_gate):
                    thru_gate = sum(thru_gate) / float(len(thru_gate))
                else:
                    thru_gate = np.NaN
            else:
                thru_gate = None
            if thru_gate is None:
                marker = 's'
                conclusion = ''
            elif thru_gate == 1:
                marker = 'D'
                conclusion = ' (good)'
            elif thru_gate == 0:
                marker = '+'
                conclusion = ' (missed)'
            else:
                marker = 'x'
                conclusion = f' ({1 - thru_gate}% missed)'

            # Do the actual plot
            tmp = ax.plot([g['r1'], g['r2']], [g['z1'], g['z2']], marker=marker, linestyle='-', lw=0.2, alpha=0.7)
            ax.text(
                g['r1'],
                g['z1'],
                f' {name}{conclusion} (for {lsurf})',
                ha='left',
                va='top',
                color=tmp[0].get_color(),
                alpha=1 if thru_gate else self.bad_alpha,
                fontdict=None if thru_gate else self.bad_style,
            )
        return ax

    def plot_boundary_points(self, slice_index=0, ax=None):
        """
        Plots reference or target points along the boundary outline

        :param slice_index: int

        :param ax: Axes instance
        """
        if ax is None:
            fig, ax = self.new_fig(slice_index=slice_index)

        t = self.ods['equilibrium.time_slice'][slice_index]['time']
        theta = np.linspace(0, 2 * np.pi, 61)
        d = 0.12

        # Combine boundary points and strike points
        bps = [
            self.ods['pulse_schedule.position_control.boundary_outline'][bpi]
            for bpi in self.ods['pulse_schedule.position_control.boundary_outline']
        ]
        sps = [
            self.ods['pulse_schedule.position_control.strike_point'][spi]
            for spi in self.ods['pulse_schedule.position_control.strike_point']
        ]
        is_strike = [False] * len(bps) + [True] * len(sps)
        bps += sps

        # Loop over boundary and strike points and deal with them
        for i, bp in enumerate(bps):
            bpn = bp['r.reference_name'] + (' (strike point)' if is_strike[i] else '')
            if 'boundary_points' in self.results:
                norm_dist = self.results['boundary_points'][slice_index].get(bpn, None)
            else:
                norm_dist = None
            if norm_dist is None:
                marker = '*'
                conclusion = ''
                fontdict = None
                alpha = 1
            elif norm_dist <= 1:
                marker = '.'
                conclusion = f' {norm_dist*100:0.1f}%'
                fontdict = None
                alpha = 1
            else:
                marker = 'x'
                conclusion = f' {norm_dist*100:0.1f}%'
                fontdict = self.bad_style
                alpha = self.bad_alpha

            rref = bp['r.reference']
            zref = bp['z.reference']
            r = interp1d(rref['time'], nominal_values(rref['data']), bounds_error=False, fill_value=np.NaN)(t)
            z = interp1d(zref['time'], nominal_values(zref['data']), bounds_error=False, fill_value=np.NaN)(t)
            r_err = interp1d(rref['time'], std_devs(rref['data']), bounds_error=False, fill_value=np.NaN)(t)
            z_err = interp1d(zref['time'], std_devs(zref['data']), bounds_error=False, fill_value=np.NaN)(t)

            # Mark the center of the point
            mark1 = ax.plot(r, z, marker=marker, alpha=0.7)
            # Ellipse with size indicating tolerance
            ax.plot(r + r_err * np.cos(theta), z + z_err * np.sin(theta), color=mark1[0].get_color(), alpha=alpha)
            # Crosshairs, to help find very small ellipses
            ax.plot(r + np.array([-d, d, np.NaN, 0, 0]), z + np.array([0, 0, np.NaN, -d, d]), color=mark1[0].get_color(), alpha=alpha)
            ax.text(
                r,
                z,
                f'{bpn}{conclusion}',
                va='bottom',
                ha='left' if 'angle_enforcer' in bpn else 'right',
                color=mark1[0].get_color(),
                fontdict=fontdict,
                alpha=alpha,
            )
        return ax

    def plot_x_points(self, slice_index=0, ax=None):
        """
        Plots X-points and reference X-points

        :param slice_index: int

        :param ax: Axes instance
        """

        if ax is None:
            fig, ax = self.new_fig(slice_index=slice_index)

        theta = np.linspace(0, 2 * np.pi, 61)
        d = 0.12

        # Mark the measured X-points
        t = self.ods['equilibrium.time_slice'][slice_index]['time']
        for eqxi in self.ods['equilibrium']['time_slice'][slice_index]['boundary']['x_point']:
            eqx = self.ods['equilibrium']['time_slice'][slice_index]['boundary']['x_point'][eqxi]
            ax.plot(eqx['r'], eqx['z'], marker='x', mew=self.fatline, markersize=self.bigmark, zorder=0, alpha=0.5)

        # Loop through reference X-points and deal with them
        for xpi in self.ods['pulse_schedule.position_control.x_point']:
            xp = self.ods['pulse_schedule.position_control.x_point'][xpi]
            xpn = xp['r.reference_name']
            if 'x_points' in self.results:
                norm_dist = self.results['x_points'][slice_index].get(xpn, None)
            else:
                norm_dist = None
            if norm_dist is None:
                marker = '*'
                conclusion = ''
                fontdict = None
                alpha = 1
            elif norm_dist <= 1:
                marker = '+'
                conclusion = f' {norm_dist*100:0.1f}%'
                fontdict = None
                alpha = 1
            else:
                marker = 'x'
                conclusion = f' {norm_dist*100:0.1f}%'
                fontdict = self.bad_style
                alpha = self.bad_alpha

            rref = xp['r.reference']
            zref = xp['z.reference']
            r = interp1d(rref['time'], nominal_values(rref['data']), bounds_error=False, fill_value=np.NaN)(t)
            z = interp1d(zref['time'], nominal_values(zref['data']), bounds_error=False, fill_value=np.NaN)(t)
            r_err = interp1d(rref['time'], std_devs(rref['data']), bounds_error=False, fill_value=np.NaN)(t)
            z_err = interp1d(zref['time'], std_devs(zref['data']), bounds_error=False, fill_value=np.NaN)(t)

            mark1 = ax.plot(r, z, marker=marker, alpha=0.7, markersize=self.bigmark)
            ax.plot(r + r_err * np.cos(theta), z + z_err * np.sin(theta), color=mark1[0].get_color(), alpha=alpha, lw=self.fatline)
            ax.plot(r + np.array([-d, d, np.NaN, 0, 0]), z + np.array([0, 0, np.NaN, -d, d]), color=mark1[0].get_color(), alpha=alpha)
            ax.text(
                r,
                z,
                f'{xpn} X-point{conclusion}',
                va='bottom',
                ha='left' if 'angle_enforcer' in xpn else 'right',
                color=mark1[0].get_color(),
                fontdict=fontdict,
                alpha=alpha,
            )

        return ax

    def plot(self, slice_index=0, ax=None):
        """
        Plots the equilibrium cross section with shape targets marked

        Instead of the standard equilibrium cross section plot supplied by OMAS,
        the high resolution contours generated for the grading process are shown.

        :param slice_index: int
            Which slice should be shown?

        :param ax: Axes instance
            Plot on these axes, if supplied.
            Otherwise, create a new figure and set up cornernote and axes scale.
        """
        track = {'p_contours_shown': [], 'r_contours_shown': []}

        # Set up axes, if needed
        if ax is None:
            fig, ax = self.new_fig(slice_index=slice_index)

        # General overlays and annotations
        rwall = self.ods['wall']['description_2d'][0]['limiter']['unit'][0]['outline']['r']
        zwall = self.ods['wall']['description_2d'][0]['limiter']['unit'][0]['outline']['z']
        ax.plot(rwall, zwall, color='k')
        rmidout, zmaxis = self.find_midplane(slice_index=slice_index)
        ax.plot(rmidout, zmaxis, marker='h', color='b', label='Outboard midplane')

        # Plot overlays for specific types of constraints
        self.plot_hires_eq(slice_index=slice_index, ax=ax, psin=1, track=track)
        self.plot_flux_gates(slice_index=slice_index, ax=ax, track=track)
        self.plot_boundary_points(slice_index=slice_index, ax=ax)
        self.plot_x_points(slice_index=slice_index, ax=ax)
        ax.legend(loc=0, numpoints=1)

        return ax

    def __call__(self):
        if not hasattr(self, 'results'):
            self.grade()
        return self.results

    def grade(self, simple_x_point_mapping=True):
        """
        Primary method for grading equilibrium shape conformity to reference shape.

        Results are placed in self.results and also returned

        :param simple_x_point_mapping: bool
            True: Use simple mapping of measured X-points to targets: just find
                closest X-point to each target.
            False: Try hard to sort X-points into primary (psin=1) and secondary
                (psin > 1) and only compare primary targets to primary measurements.

        :return: dict
            Dictionary of results, with one key per category
        """
        self.results['boundary_points'] = self.grade_boundary_points()
        self.results['x_points'] = self.grade_x_points(simple_map=simple_x_point_mapping)
        self.results['flux_gates'] = self.grade_gates()

        return self.results

    def grade_x_points(self, improve_xpoint_measurement=True, simple_map=True, psin_tolerance_primary=5e-4):
        """
        Grades conformity of X-point position(s) to specifications

        :param improve_xpoint_measurement: bool

        :param simple_map: bool
            For each target, just find the closest measured X-point and compare.
            Requires at least as many measurements as targets and raises OmasUtilsBadInput if not satisfied.

        :param psin_tolerance_primary: float
            Tolerance in psin for declaring an X-point to be on the primary separatrix

        :return: list of dicts
            One list element per time-slice.
            Within each dictionary, keys give labels for X-point targets, and values
                give normalized distance errors.
        """
        from omfit_classes.omfit_eqdsk import x_point_search

        if self.debug_out is not None:
            out = self.debug_out[f'grade_x_points_{"simple" if simple_map else "map"}'] = self.debug_out.__class__()
            out['zoomed_eq_sample'] = self.zoomed_eq(slice_index=0)
        else:
            out = None

        # Make sure inputs are ready and abort early if not
        if len(self.ods['pulse_schedule.position_control.x_point']) < 1:
            self.printdq('No X-points references are defined in specifications. Skip grading X-points.')
            return []

        # Get measured X-points
        t = self.ods['.equilibrium.time']
        xr = copy.deepcopy(self.ods['equilibrium.time_slice.:.boundary.x_point.:.r'])
        xz = copy.deepcopy(self.ods['equilibrium.time_slice.:.boundary.x_point.:.z'])
        nxm = len(xr[0, :])
        self.printdq('  Processing measured X-point positions...')
        if improve_xpoint_measurement:
            rr = copy.copy(xr)
            zr = copy.copy(xz)
            for i in range(len(t)):
                rg, zg, pzoom = self.zoomed_eq(slice_index=i)
                if out is not None:
                    out['rg'] = rg
                    out['zg'] = zg
                    out[f'pzoom{i}'] = pzoom
                for j in range(nxm):
                    psin_at_x = interp2d(rg, zg, pzoom.T)(xr[i, j], xz[i, j])
                    xr_, xz_ = x_point_search(rg, zg, pzoom.T, r_center=rr[i, j], z_center=zr[i, j], zoom=3)
                    if np.isnan(xr_) or np.isnan(xz_):
                        self.printdq(
                            f'    Did not find a primary xpoint near {xr[i, j]}, {xz[i, j]}; '
                            f'setting psi_boundary_weight=0 and trying again.'
                        )
                        xr_, xz_ = x_point_search(rg, zg, pzoom.T, r_center=rr[i, j], z_center=zr[i, j], zoom=3, psi_boundary_weight=0)
                    if ~np.isnan(xr_) and ~np.isnan(xz_):
                        xr[i, j], xz[i, j] = xr_, xz_
                    self.printdq(
                        f'    xpointsearch {i}, {j} centered at {rr[i, j]}, {zr[i, j]} '
                        f'(psin = {psin_at_x} here) found xpoint at {xr[i, j]}, {xz[i, j]}'
                    )

        # Get target X-points
        pc = self.ods['pulse_schedule.position_control']
        xrtt = pc['x_point.:.r.reference.time'].T
        nxt = len(xrtt[0, :])
        xrtd = nominal_values(pc['x_point.:.r.reference.data']).T
        xrte = std_devs(pc['x_point.:.r.reference.data']).T
        ikw0 = dict(bounds_error=False, fill_value=np.NaN, axis=0)
        if nxt < 2 or np.nanmax(np.diff(xrtt, axis=1)) == 0:
            xrt = interp1d(xrtt[:, 0], xrtd, **ikw0)(t)
            xrt_err = interp1d(xrtt[:, 0], xrte, **ikw0)(t)
        else:
            xrt = [interp1d(xrtt[:, i], xrtd[:, i], **ikw0)(t) for i in range(nxt)]
            xrt_err = [interp1d(xrtt[:, i], xrte[:, i], **ikw0)(t) for i in range(nxt)]
        xztt = pc['x_point.:.z.reference.time'].T
        xztd = nominal_values(pc['x_point.:.z.reference.data'].T)
        xzte = std_devs(pc['x_point.:.z.reference.data'].T)
        if nxt < 2 or np.nanmax(np.diff(xztt, axis=1)) == 0:
            xzt = interp1d(xztt[:, 0], xztd, **ikw0)(t)
            xzt_err = interp1d(xztt[:, 0], xzte, **ikw0)(t)
        else:
            xzt = [interp1d(xztt[:, i], xztd[:, i], **ikw0)(t) for i in range(nxt)]
            xzt_err = [interp1d(xztt[:, i], xzte[:, i], **ikw0)(t) for i in range(nxt)]
        nt = len(t)

        if self.debug_out is not None:
            self.printdq(f'xrtt = {xrtt}')
            self.printdq(f'np.diff(xrtt, axis=1) = {np.diff(xrtt, axis=1)}')
            out['t'] = t
            out['nxt'] = nxt
            out['xrtt'] = xrtt
            out['xztt0'] = xztt[:, 0]
            out['xrtd'] = xrtd
            out['xztd'] = xrtd
            out['xrt'] = xrt
            out['xzt'] = xzt
            out['xr'] = xr
            out['xz'] = xz

        if simple_map:
            # Mapping X-points is hard! Let's just pick the closest measurement to each target.
            if nxt > nxm:
                raise OmasUtilsBadInput("Simple mapping requires at least as many measured X-points as targets.")
            dxr = np.nanmin(abs(xr[:, :, np.newaxis] - xrt[:, np.newaxis, :]), axis=1)
            dxz = np.nanmin(abs(xz[:, :, np.newaxis] - xzt[:, np.newaxis, :]), axis=1)
        else:
            # Now we must map which measured X-point goes with which target. They might not all have targets.

            # Map target X-points. There can be more than one on a surface in case of double null or snowflake.
            primary_xt = []
            secondary_xt = []
            unidentified_xt = list(range(nxt))
            for i in copy.copy(unidentified_xt):
                x = pc['x_point'][i]
                named_primary = 'primary' in repr(x['r.reference_name']).lower() + repr(x['z.reference_name']).lower()
                if named_primary:
                    primary_xt += [i]
                    unidentified_xt.remove(i)
            for i in copy.copy(unidentified_xt):
                x = pc['x_point'][i]
                named_sec = 'secondary' in repr(x['r.reference_name']).lower() + repr(x['z.reference_name']).lower()
                if named_sec:
                    secondary_xt += [i]
                    unidentified_xt.remove(i)
            if len(unidentified_xt) > 0 and nxt == 1:
                # There is only one target, so it's pretty safe to assume it's for the primary x-point.
                # If you don't like this assumption, name your single X-point with "secondary" in reference_name.
                primary_xt += [0]
                unidentified_xt.remove(0)
            if len(unidentified_xt) > 0:
                printw(
                    'WARNING! Failed to identify all the X-point targets as primary or secondary. '
                    'The unidentified ones might be treated as secondary.'
                )

            # Map measured X-points. It's trickier since mapping between primary/secondary & top/bottom can switch.
            is_primary = np.zeros((nt, nxm), bool)
            for it in range(nt):
                # Get normalized psi values interpolated from the upsampled flux map to the X-point locations
                rgrid, zgrid, psingrid = self.zoomed_eq(slice_index=0)
                psin_x = np.array([interp2d(rgrid, zgrid, psingrid.T)(xr[it, j], xz[it, j])[0] for j in range(len(xr[it, :]))])
                # Could a given X-point be the primary? Must be very close to psin = 1
                close_psin = abs(psin_x - 1) < psin_tolerance_primary
                smallest_delta_this_slice = np.nanmin(abs(psin_x - 1))
                # Could there be more than one primary X-point (balanced DN or snowflake)?
                # To qualify, the two X-points would have to be about the same distance from psin = 1
                close_to_minimum_delta = (abs(psin_x - 1) / smallest_delta_this_slice) < 1.2
                # What if the errors go in opposite directions? As in, one X-point's psin estimate is slightly < 1?
                close_to_minimum_psin_x = (psin_x - np.nanmin(psin_x)) < psin_tolerance_primary
                if self.debug_out is not None:
                    out[f'psin_x_{it}'] = psin_x
                    out[f'close_psin_{it}'] = close_psin
                    out[f'smallest_delta_this_slice_{it}'] = smallest_delta_this_slice
                    out[f'close_to_minimum_delta_{it}'] = close_to_minimum_delta
                    out[f'close_to_minimum_psin_x_{it}'] = close_to_minimum_psin_x
                is_primary[it, :] = close_psin & close_to_minimum_delta & close_to_minimum_psin_x

            # Now do the comparison, but only primary targets vs primary X-points, and only secondary vs secondary.
            target_primary = np.zeros((nt, nxt), bool)
            for i in primary_xt:
                target_primary[:, i] = True
            compare_okay = is_primary[:, :, np.newaxis] == target_primary[:, np.newaxis, :]

            bigboy = 1e8
            dxr = np.nanmin(abs(xr[:, :, np.newaxis] - xrt[:, np.newaxis, :]) + ~compare_okay * bigboy, axis=1)
            dxz = np.nanmin(abs(xz[:, :, np.newaxis] - xzt[:, np.newaxis, :]) + ~compare_okay * bigboy, axis=1)
            dxr[dxr >= bigboy] = np.NaN
            dxz[dxz >= bigboy] = np.NaN

            if self.debug_out is not None:
                out['compare_okay'] = compare_okay
                out['is_primary'] = is_primary
                out['target_primary'] = target_primary
                out['dxr'] = dxr
                out['dxz'] = dxz

        real_dist = np.sqrt(dxr ** 2 + dxz ** 2)
        no_norm = np.nanmax(abs(xrt_err)) == 0 or np.nanmax(abs(xzt_err == 0))
        if no_norm:
            printw(
                "All X-point R or Z position uncertainties were 0; skipping normalization to "
                "uncertainty/tolerance. Errors will be reported in data units instead. Now you can't "
                "compare errors with different units: remember that you've done this to yourself."
            )
            norm_dist = real_dist
        else:
            norm_dist = np.sqrt((dxr / xrt_err) ** 2 + (dxz / xzt_err) ** 2)

        for it in range(nt):
            eqt = self.ods['equilibrium.time'][it]
            print(f'  Conformity of X-point positions to specs for equilibrium slice {it} at t={eqt:0.3f} s:')
            for ix in range(nxt):
                xpt = self.ods['pulse_schedule.position_control.x_point'][ix]
                xpn = xpt['r.reference_name']
                if no_norm:
                    print(f'    The error at X-point {xpn} is {real_dist[it, ix]:0.3f} {self.units}')
                else:
                    print(
                        f'    The error at X-point {xpn} is {norm_dist[it, ix] * 100:0.1f}% of tolerance: '
                        f'{"okay" if norm_dist[it, ix] < 1 else "BAD!!"}'
                    )

        if self.debug_out is not None:
            out['norm_dist'] = norm_dist
            out['real_dist'] = real_dist
            out['xrt_err'] = xrt_err
            out['xzt_err'] = xzt_err

        return [
            {pc['x_point'][j]['r.reference_name']: norm_dist[i, j] for j in range(len(norm_dist[0, :]))}
            for i in range(len(norm_dist[:, 0]))
        ]

    def grade_boundary_points(self):
        """
        Grades proximity of boundary to target boundary points

        We need a high resolution flux surface contour for each time slice, so
        I think we have to loop and upsample each one individually.
        """
        results = []
        for slice_index in self.ods['equilibrium']['time_slice']:
            t = self.ods['equilibrium']['time_slice'][slice_index]['time']
            print(f'  Checking boundary points for equilibrium slice {slice_index} at t={t}')
            results += [self.grade_boundary_points_slice(slice_index=slice_index)]
        return results

    def grade_boundary_points_slice(self, slice_index=0):
        """
        Grades proximity of boundary to target boundary points for a specific time-slice of the equilibrium

        Strike points are included and treated like other boundary points
        (except they get a note appended to their name when forming labels).

        There can be differences in the exact wall measurements (such as attempts to
        account for toroidal variation, etc.) that cause a strike point measurement
        or specification to not be on the reported wall. Since I can't think of a way
        to enforce consistent interpretation of where the wall is between the strike
        point specification and the measured equilibrium, I've settled for making sure
        the boundary goes through the specified strike point. This could go badly if
        the contour segment passing through the specified strike point were disconnected
        from the core plasma, such as if it limited or something. I'm hoping to get away
        with this for now, though.

        :param slice_index: int
            Number of the time-slice to consider for obtaining the LCFS.
        """
        results = {}
        contours = self.hires_contour(slice_index=slice_index)
        pc = self.ods['pulse_schedule.position_control']

        the_boundary_points = [pc['boundary_outline'][i] for i in pc['boundary_outline']]
        the_strike_points = [pc['strike_point'][i] for i in pc['strike_point']]
        the_points = the_boundary_points + the_strike_points
        is_strike = [False] * len(the_boundary_points) + [True] * len(the_strike_points)

        for i in range(len(the_points)):
            bpn = the_points[i]['r.reference_name'] + (' (strike point)' if is_strike[i] else '')
            self.printdq(f'    Now checking boundary point {bpn}...')
            bpr = the_points[i]['r.reference.data']
            bpz = the_points[i]['z.reference.data']
            # Get normalization constants
            bpr_err = std_devs(bpr)
            bpz_err = std_devs(bpz)
            both_zero = (bpr_err == 0) & (bpz_err == 0)
            bpr_err[both_zero] = 1
            bpz_err[both_zero] = 1
            if any(both_zero):
                printw(
                    f'Warning: uncertainties (used as tolerances) are 0 for {bpn} for {sum(both_zero)} points '
                    f'out of {len(bpr_err)}. Errors are not being normalized to tolerances for these points.'
                )
                no_norm = True
            else:
                no_norm = False
            bpr_zero = (bpr_err == 0) & (bpz_err != 0)
            # Make the R tolerance non-zero but much smaller than Z tolerance
            bpr_err[bpr_zero] = bpz_err[bpr_zero] / 1e16
            bpz_zero = (bpz_err == 0) & (bpr_err != 0)
            bpz_err[bpz_zero] = bpr_err[bpz_zero] / 1e16

            norm_dist = []
            for c_sec in contours:
                # Assume the boundary is high enough resolution that we can do distance the lazy way
                # min_dist = np.sqrt(np.nanmin((c_sec[:, 0] - bp['r']) ** 2 + (c_sec[:, 1] - bp['z']) ** 2))
                # I don't trust the lazy way, so do it nicely
                norm_dist2 = []
                for j in range(len(c_sec[:, 0]) - 1):
                    # Do the distance to line in normalized coordinates instead of data units
                    cpr, cpz = point_to_line(
                        nominal_values(bpr) / bpr_err,
                        nominal_values(bpz) / bpz_err,
                        c_sec[j, 0] / bpr_err,
                        c_sec[j, 1] / bpz_err,
                        c_sec[j + 1, 0] / bpr_err,
                        c_sec[j + 1, 1] / bpz_err,
                        return_closest_point=True,
                    )
                    # Normalized distances for this point to each segment of this section of this contour
                    ndr = nominal_values(bpr) / bpr_err - cpr
                    ndz = nominal_values(bpz) / bpz_err - cpz
                    norm_dist2 += [np.sqrt(ndr ** 2 + ndz ** 2)]
                # Normalized distance for this point to the closest segment of this section of this contour
                norm_dist += [np.nanmin(norm_dist2)]
            # Normalized distance for this point to the closest segment of the closest section of this contour
            # AKA minimum distance from this point to any part of the contour.
            norm_dist = np.min(norm_dist)
            if no_norm:
                data_units = 'm'  # TODO: read this from OMAS
                print(f'    The error at point {bpn} is {norm_dist} {data_units}')
            else:
                print(
                    f'    The error at point {bpn} is {norm_dist * 100:0.1f}% of tolerance: '
                    f'{"acceptable." if norm_dist < 1 else "BAD!"}'
                )
            results[f'{bpn}'] = norm_dist
        return results

    def grade_gates(self):
        """Grades boundary on passing through 'gates': pairs of points"""
        results = []
        for slice_index in self.ods['equilibrium']['time_slice']:
            t = self.ods['equilibrium']['time_slice'][slice_index]['time']
            print(f'  Checking boundary gates for equilibrium slice {slice_index} at t={t}')
            results += [self.grade_gates_slice(slice_index=slice_index)]
        return results

    def grade_gates_slice(self, slice_index=0):
        """Grades flux surfaces on passing through 'gates' (pairs of points) at a specific time-slice"""
        results = {}
        pc = self.ods['pulse_schedule.position_control']

        for i in pc['flux_gates']:
            bg = pc['flux_gates'][i]
            bgn = bg['name']
            self.printdq(f'    Now checking boundary gate {bgn}...')
            time_range = bg.get('time_range', None)
            if (time_range is None) or (time_range[0] >= time_range[1]):
                self.printdq(f'  Flux gate {bgn} does not have a specified time range, so it applies to all times.')
            else:
                eqt = self.ods['equilibrium.time'][slice_index]
                slice_in_range = time_range[0] <= eqt <= time_range[1]
                if not slice_in_range:
                    print(f'  Flux gate {bgn} does not apply to time slice {slice_index} at {eqt} s')
                    continue
            gate_path = np.array([[bg['r1'], bg['r2']], [bg['z1'], bg['z2']]]).T

            cvals_psin = np.atleast_1d(bg.get('applies_to_psin', []))
            cvals_rmid = np.atleast_1d(bg.get('applies_to_dr_mid', []))
            contour_count = len(cvals_psin) + len(cvals_rmid)
            if contour_count == 0:
                cvals_psin = [1]
            # There's caching within the methods for obtaining flux surfaces, so they can be reused by a bunch
            # of gates in this loop without too much of a speed penalty.
            all_contours = [self.hires_contour(slice_index=slice_index, psin=psin) for psin in cvals_psin] + [
                self.find_fluxsurface(slice_index=slice_index, midplane_dr=dr) for dr in cvals_rmid
            ]
            contour_labels = [f'psin={psin:0.3f}' for psin in cvals_psin] + [f'dR_mid={dr}' for dr in cvals_rmid]
            for contours, label in zip(all_contours, contour_labels):
                intersects = False
                for c_sec in contours:
                    if len(line_intersect(c_sec, gate_path)):
                        intersects = True
                if intersects:
                    conclusion = 'passes'
                else:
                    if bg.get('critical', True):
                        conclusion = 'DOES NOT PASS'
                    else:
                        conclusion = 'does not pass'
                print(f'    Flux surface {label} {conclusion} through gate {bgn}')
                results[f'{label} surface thru {bgn}'] = intersects
        return results

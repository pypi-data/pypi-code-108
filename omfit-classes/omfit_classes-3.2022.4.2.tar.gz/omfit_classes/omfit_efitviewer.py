# -*-Python-*-
# Created by eldond at 2019-12-23 08:56

"""
Contains supporting functions to back the efitviewer GUI
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

import omas
from omas import ODS
from omfit_classes.omfit_base import OMFITtmp, OMFITmodule, OMFITtree
from omfit_classes.omfit_json import OMFITjson, OMFITsettings, SettingsName
from omfit_classes.omfit_omas_utils import setup_hardware_overlay_cx, add_hardware_to_ods, omas_eq1d_pretty_name
from omfit_classes.omfit_formatter import omfit_formatter
from omfit_classes.utils_fusion import is_device
from omfit_classes.omfit_mds import translate_MDSserver

__all__ = ['efitviewer']

# Provide better plot limits than autoscale, which might cut off some external hardware like magnetic probes
default_plot_limits = {'DIII-D': {'x': [0.75, 2.75], 'y': [-1.75, 1.75]}, 'EAST': {'x': [0.55, 3.4], 'y': [-2.1, 2.1]}}

# List of features and the OMAS version required to use them
omas_features = {
    'contour_quantity': '0.50.0',
    'allow_fallback': '0.50.0',
    'sf': '0.50.0',
    'label_contours': '0.50.0',
    'show_wall': '0.55.2',
    'xkw': '0.52.2',
}


class EfitviewerDataError(doNotReportException, ValueError):
    """There is a problem with the data needed to make efitviewer work"""


# Shortcuts and utilities for defining key information, data structure, and shortcuts -----------------------------
def efitviewer():
    """Shortcut for launching efitviewer"""
    OMFIT['scratch']['__efitviewer_gui__'].run()
    return


def pick_output_location():
    """
    Selects efitviewer output folder for storing ODSs and settings

    :return (string, string, dict-like, dict-like, dict-like, dict-like)
        Location in the tree of the output folder
        Location in the tree of the settings dictionary
        Reference to output folder in the tree
        Reference to efitviewer settings
        Reference to settings in the local parent module or main OMFIT settings
        Reference to main scratch area
    """
    default_out_loc = "OMFIT['efitviewer']"
    scratch = OMFIT['scratch']
    override_loc = scratch.get('efitviewer_out_loc', None)

    # Resolve output location
    if override_loc is None:
        out_loc = default_out_loc
        printd('No output_loc supplied; using default')
    elif not (is_string(evalExpr(override_loc))):
        out_loc = default_out_loc
        printd('output_loc is not a string; using default loc instead')
    else:
        out_loc = output_loc
        printd('assuming user-supplied output_loc is valid')

    # Make sure the output loc exists
    the_split = out_loc.split('[')
    locations = ['['.join(the_split[:i]) for i in range(1, len(the_split) + 1)]
    for i in range(1, len(locations)):
        key = locations[i].split('[')[-1].split(']')[0]
        key = key.split(key[0])[1]  # Remove quotes, regardless of whether ' or " is used
        the_parent = eval(locations[i - 1])
        if key not in the_parent:
            if isinstance(the_parent, OMFITtmp):
                # Items added under OMFITtmp should be OMFITtree
                key_type = OMFITtree
            elif isinstance(the_parent, OMFITjson):
                # Items under OMFITjson should be SortedDict
                key_type = SortedDict
            elif isinstance(the_parent, OMFITsettings):
                # Items under OMFITsettings should be SettingsName
                key_type = SettingsName
            elif type(the_parent).__name__ in ['OMFITmaintree']:
                # OMFITmaintree might not be defined in this context
                key_type = OMFITtree
            elif type(the_parent).__name__ in ['OMFITtree', 'dict', 'SettingsName', 'SortedDict']:
                # Copy class of parent if parent's class is appropriate
                key_type = type(the_parent)
                printd('pick_output_location(): copy parent type', topic='efitviewer')
            else:
                # Otherwise, default to SortedDict
                key_type = SortedDict
                printd('pick_output_location(): we do not like this type; just use SortedDict', topic='efitviewer')

            printd(f'pick_output_location(): type(parent)={type(the_parent)}&type(key)={key_type}', topic='efitviewer')
            the_parent[key] = key_type()

    out = eval(out_loc)

    # Make sure settings are defined and load defaults if needed
    if 'SETTINGS' not in out:
        out['SETTINGS'] = OMFITsettings(os.sep.join([OMFITsrc, 'framework_guis', 'efitviewer_settings.txt']))
    settings_loc = out_loc + "['SETTINGS']"
    settings = eval(settings_loc)

    # Also get a reference to parent module or main OMFIT settings
    for loc in locations[::-1]:
        ppm = eval(loc)
        if (isinstance(ppm, OMFITmodule) and ('SETTINGS' in ppm)) or ('MainSettings' in ppm):
            parent_settings = ppm['SETTINGS'] if 'SETTINGS' in ppm else ppm['MainSettings']
            break
    else:
        parent_settings = MainSettings

    return out_loc, settings_loc, out, settings, parent_settings, scratch


def add_command_box_tab():
    """
    Adds a tab to the command box. Useful if the user wants output dumped to a new tab.

    :return: int
        Index of the new command box tab that has been added
    """
    number = len(OMFITaux['GUI'].command)
    OMFITaux['GUI'].commandAdd(number)
    OMFITaux['GUI'].commandNotebook.select(OMFITaux['GUI'].commandNotebook.tabs().index(OMFITaux['GUI'].commandNotebook.select()))
    return number


# Data loading and related helpers --------------------------------------------------------------------------------
def parse_load_cx_ods_kw(
    gfile=None, device=None, shot=None, t=None, efitid=None, index=0, no_empty=None, settings=None, minimal_eq_data=None
):
    """
    Handles setting defaults for keywords to load_cx_ods()

    Keeps load_cx_ods() simpler and allows isolated testing. load_cx_ods() is
    called by GUI buttons, and OMFIT GUIs are difficult to test. So, this helps
    accomplish some limited GUI testing.

    :param kw: keywords passed to load_cx_ods

    :return: tuple containing
        gfile: OMFITgeqdsk or None
        device: str
        shot: int
        efitid: str
        no_empty: bool
        ods_tag: str
    """
    if settings is None:
        _, _, _, settings, _, _ = pick_output_location()
    the_case = settings['cases'][index]
    def_def_gfile = settings['cases'][0]['gfile']
    def_def_device = tokamak(settings['cases'][0]['device'])
    def_def_shot = evalExpr(settings['cases'][0]['shot'])
    if index == 0:
        ods_tag = 'efitviewer_ods'
        def_device = def_def_device
        def_shot = def_def_shot
        def_gfile = def_def_gfile
    else:
        ods_tag = 'efitviewer_ods_{}'.format(index)
        def_device = the_case.setdefault('device', def_def_device)
        def_shot = the_case.setdefault('shot', def_def_shot)
        def_gfile = the_case.setdefault('gfile', def_def_gfile)

    if gfile is None:
        gfile = def_gfile
    if gfile == 'unused':
        gfile = None
    if device is None:
        device = def_device
    if shot is None:
        shot = def_shot
    if efitid is None:
        efitid = the_case.setdefault('efit_tree', None)
    if no_empty is None:
        no_empty = settings.setdefault('no_empty', True)
    if minimal_eq_data is None:
        minimal_eq_data = settings.setdefault('minimal_eq_data', True)

    return gfile, device, shot, efitid, no_empty, minimal_eq_data, ods_tag


def load_cx_ods(gfile=None, device=None, shot=None, t=None, efitid=None, index=0, no_empty=None, minimal_eq_data=None):
    """
    Puts an ODS with CX info in the tree

    :param gfile: OMFITgeqdsk instance [optional if shot, t, and efitid are supplied]
        Pass in 'unused' to prevent None from being used as an instruction to seek out a default value.

    :param device: string

    :param shot: int [ignored if gfile is supplied]

    :param t: int [ignored if gfile is supplied]
        Leave it as None to load minimal data for all slices,
        or specify a single time to load just one complete slice

    :param efitid: string [ignored if gfile is supplied]

    :param index: int
        Index of the ODS, for managing multi-shot overlays

    :param no_empty: bool
        Filter out equilibrium time-slices that have 0 current or 0 boundary outline points.
        (this is passed to multi_efit_to_omas() via setup_hardware_overlay_cx())

    :minimal_eq_data: bool
        If the source is MDSplus, load only the minimal dataset needed to power the equilibrium cross section plot.

    :return: ODS instance
    """
    printd(f'  loading cx ods for index {index}', topic='omfit_efitviewer')
    _, _, out, settings, _, _ = pick_output_location()
    gfile, device, shot, efitid, no_empty, minimal_eq_data, ods_tag = parse_load_cx_ods_kw(
        gfile=gfile,
        device=device,
        shot=shot,
        t=t,
        efitid=efitid,
        index=index,
        no_empty=no_empty,
        settings=settings,
        minimal_eq_data=minimal_eq_data,
    )

    if isinstance(gfile, str):
        gfile_str = gfile
        gfile = eval(gfile)
    elif gfile is not None:
        gfile_str = '<<YOUR G-FILE FOR {device:}:{gfilename:}>>'.format(device=device, gfilename=gfile.filename)
    else:
        gfile_str = None

    if gfile is None:
        load_cmd = "setup_hardware_overlay_cx({}, {}, {}, efitid={}, default_load=False, no_empty={}, minimal_eq_data={})".format(
            repr(device), repr(shot), repr(t), repr(efitid), no_empty, minimal_eq_data
        )
        ods = out[ods_tag] = setup_hardware_overlay_cx(
            device, shot, t, efitid=efitid, default_load=False, quiet=True, no_empty=no_empty, minimal_eq_data=minimal_eq_data
        )
        ods['dataset_description.ids_properties.source'] = 'MDSplus'
    else:
        printd(f' Using a gfile or set with type {type(gfile)} to setup cx data.', topic='omfit_efitviewer')
        ods = out[ods_tag] = setup_hardware_overlay_cx(
            device, geqdsk=gfile, default_load=False, quiet=True, no_empty=no_empty, minimal_eq_data=minimal_eq_data
        )
        load_cmd = "setup_hardware_overlay_cx({}, geqdsk={}, default_load=False, no_empty={}, minimal_eq_data={})".format(
            repr(device), gfile_str, no_empty, minimal_eq_data
        )
        ods['dataset_description.ids_properties.source'] = gfile_str

    settings['cases'][index]['instructions_for_loading_ods'] = load_cmd
    if 'equilibrium' not in ods or 'time' not in ods['equilibrium']:
        error_message = (
            f'\nFailed to populate equilibrium data in the ODS.\n'
            f'This can happen if the data are missing from the\n'
            f'source database or if there is a connection problem.\n'
            f'You can try "File" > "Reset SSH tunnels, database connections".\n'
            f'If that does not work, please verify access to the database\n'
            f'({translate_MDSserver(device, efitid)})\n'
            f'and check that the shot ({device}#{shot}) has data for {efitid}.'
        )
        ods['dataset_description.ids_properties.comment'] = error_message
        raise EfitviewerDataError(error_message)

    return ods


def list_available_hardware_descriptors(device):
    """
    Determines which hardware systems have descriptor functions available.

    That is, which systems can easily have their geometry loaded into an ODS?

    :param device: string

    :return: list of strings
        List of formal IMAS names of hardware systems that can be easily loaded into an ODS by OMFIT
    """
    hw0 = 'setup_'
    hw1 = '_hardware_description_'
    available_hardware_d3d = [
        a.split(hw1 + 'd3d')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_d3d.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'd3d')
    ]
    available_hardware_east = [
        a.split(hw1 + 'east')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_east.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'east')
    ]
    available_hardware_kstar = [
        a.split(hw1 + 'kstar')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas_kstar.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'kstar')
    ]
    available_hardware_general = [
        a.split(hw1 + 'general')[0].split(hw0)[-1]
        for a in omfit_classes.omfit_omas.__all__
        if a.startswith(hw0) and a.endswith(hw1 + 'general')
    ]

    if is_device(device, 'DIII-D'):
        available_hardware = available_hardware_general + available_hardware_d3d
    elif is_device(device, ['EAST', 'EAST_US']):
        available_hardware = available_hardware_general + available_hardware_east
    elif is_device(device, 'KSTAR'):
        available_hardware = available_hardware_general + available_hardware_kstar
    else:
        available_hardware = available_hardware_general
    return available_hardware


def list_available_hardware_data(ods, systems=None):
    """
    Determines which systems appear to have valid geometry data in ODS and could probably be overlaid in efitviewer.

    :param ods: ODS instance

    :param systems: list of strings
        List of formal IMAS names of hardware systems to consider in the search.
        Defaults to all keys in top level ods.

    :return: list of strings
        List of formal IMAS names of hardware systems that look like they're ready to plot using data already in ods.
    """
    if systems is None:
        systems = ods.keys()

    return [system for system in systems if len(ods.search_paths('{}.*(geometry|position|position_control)'.format(system))) > 0]


def list_hardware_overlay_methods():
    """
    Determines which hardware systems can be overlaid natively by OMAS

    :return: list of strings
        List of formal IMAS names of hardware systems that have plot overlay methods built into OMAS
    """
    a1 = 'plot_'
    a2 = '_overlay'
    return [a[len(a1) : -len(a2)] for a in dir(ODS) if a.startswith(a1) and a.endswith(a2) and a != 'plot_overlay']


def setup_avail_systems(suppress_systems=['pulse_schedule']):
    """
    Makes sure keys in systems correspond to available plot overlays in ODS

    Operates on the 0th ODS instance, not the different equilibrium overlays

    :param suppress_systems: list of strings
        Remove these systems from the list; their methods are redundant
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    systems = settings['systems']
    if 'efitviewer_ods' in out:
        ods = out['efitviewer_ods']
        device = out['efitviewer_ods']['dataset_description.data_entry'].get('machine', tokamak(settings['cases'][0]['device']))
    else:
        ods = None
        device = tokamak(settings['cases'][0]['device'])

    has_plot_method = list_hardware_overlay_methods()
    has_loader_method = list_available_hardware_descriptors(device)
    has_data = list_available_hardware_data(ods)

    overlays = has_plot_method and (has_loader_method or has_data)
    overlays = [overlay for overlay in overlays if overlay not in suppress_systems]

    for k in list(systems.keys()):
        if k not in overlays:
            systems.pop(k)
    for overlay in overlays:
        systems.setdefault(overlay, False)
    return


# Special overlays ------------------------------------------------------------------------------------------------
def plot_scaled_boundary_overlay(
    ax=None, device='ITER', mds_tree='', shot=0, time=0, scale=1 / 3.68, x_offset=0, y_offset=-0.88 / 3.68, **kw
):
    r"""
    Overlays the boundary of another device, including scaling and offsets

    :param ax: Axes instance

    :param device: string

    :param mds_tree: string

    :param shot: int

    :param time: numeric
        Time in ms

    :param scale: float

    :param x_offset: float
        Horizontal offset after scaling (m)

    :param y_offset: float
        Vertical offset after scaling (m)

    :param \**kw: Keywords to pass to plot()

    :return: output from plot()
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    kw.pop('t', None)  # t is ignored since we're choosing an overlay time from the settings under value
    kw.pop('ods', None)  # We don't need this,but we have to take it to have a consistent call signature

    if ax is None:
        ax = scratch.get('efitviewer_cx_ax', None)
    if ax is None:
        ax = gca()

    if is_device(device, 'ITER'):
        dat = np.genfromtxt(os.sep.join([OMFITsrc, '..', 'samples', 'iter_BL2010_Gribov.txt']), skip_header=3)
        r = dat[:, 0] * abs(scale) + x_offset
        z = dat[:, 1] * scale + y_offset
        label = 'Scaled ITER'
    else:
        eq_dat = read_basic_eq_from_mds(
            device=device,
            shot=shot,
            tree=mds_tree,
            g_file_quantities=['RBBBS', 'ZBBBS'],
            a_file_quantities=[],
            measurements=[],
            other_results=[],
            derived_quantities=['time'],
        )
        it = closestIndex(eq_dat['time'], time)
        r = eq_dat['RBBBS'][it, :] * scale + x_offset
        z = eq_dat['ZBBBS'][it, :] * scale + y_offset
        btime = eq_dat['time'][it]
        label = 'Scaled {}#{} @ {}'.format(device, shot, btime)

    kw.setdefault('label', label)
    return ax.plot(r, z, **kw)


def plot_beam_emission_spectroscopy_overlay(ax=None, ods=None, **kw):
    r"""
    Overlays measurement positions for the Beam Emission Spectroscopy (BES) diagnostic for DIII-D

    :param ax: Axes instance

    :param ods: ODS instance (for confirming device and getting shot)

    :param \**kw: Keywords to pass to plot, such as color, marker, etc.

    :return: output from plot() call
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if ods is None:
        ods = out.get('efitviewer_ods', None)
    if ods is None:
        return
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    if not is_device(device, 'DIII-D'):
        printe('beam_emission_spectroscopy overlay supports DIII-D only, sorry. Aborting and deactivating.')
        settings['special_systems']['beam_emission_spectroscopy'] = False
        return

    shot = ods['dataset_description.data_entry'].get('.pulse', evalExpr(settings['cases'][0]['shot']))

    if ax is None:
        ax = scratch.get('efitviewer_cx_ax', None)
    if ax is None:
        ax = gca()

    kw.pop('t', None)  # t is ignored for BES since the configuration doesn't change in time
    kw.pop('value', None)  # The BES activation flag doesn't carry special information that we need to consider

    # noinspection PyBroadException
    try:
        from omfit_classes.omfit_mds import OMFITmdsValue

        r = OMFITmdsValue(device, shot=shot, TDI='BES_R').data() / 100.0
        z = OMFITmdsValue(device, shot=shot, TDI='BES_Z').data() / 100.0
    except Exception:
        printe('BES data acquisition failed for {}#{}. Aborting and deactivating.'.format(device, shot))
        settings['special_systems']['beam_emission_spectroscopy'] = False
        report = ''.join(traceback.format_exception(*sys.exc_info()))
        printe(report)
        return
    kw.setdefault('marker', 's')
    kw.setdefault('linestyle', ' ')
    kw.setdefault('label', 'BES')
    return ax.plot(r, z, **kw)


def plot_custom_script_overlay(ax=None, ods=None, defaultvars_keywords=None, **kw):
    r"""
    Calls a script to draw a custom overlay or set of overlays.
    The script should use defaultVars() to accept the following keywords at minimum:
        ax
        ods

    :param ax: Axes instance [optional]
        If not provided, the custom script had better have a way of choosing.
        The default axes when using the efitviewer GUI are referenced in scratch.get('efitviewer_cx_ax', None)

    :param ods: ODS instance

    :param defaultvars_keywords: dict
        Keywords to pass to script's defaultVars()

    :param \**kw: additional keywords accepted to avoid problems (ignored)
    """
    if ods is None:
        out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
        ods = out.get('efitviewer_ods', None)
    script_loc = kw.pop('script_loc', None)
    if script_loc is None:
        printe('Invalid script location. Cannot call custom script overlay.')
    printd('    efitviewer lib plot_custom_script_overlay: script_loc = {}'.format(repr(script_loc)))
    script = eval(script_loc)
    if defaultvars_keywords is None:
        defaultvars_keywords = {}
    script.runNoGUI(ax=ax, ods=ods, **defaultvars_keywords)
    return


def plot_alt_limiter_overlay(ax=None, **kw):
    """
    Plots an alternative limiter overlay

    :param ax: Axes instance

    :param kw: Additional keywords

    :return: output from plot() call
    """
    # Extract kw
    ignore_kw = ['t', 'value', 'labelevery', 'notesize', 'mask', 'ods']  # Unused
    ignore_kw += ['retain_wall']  # This should be used elsewhere
    for ikw in ignore_kw:
        kw.pop(ikw, None)
    scale = kw.pop('scale', 1.0)
    alt_lim_loc = kw.pop('alt_limiter_data_loc', None)
    alt_lim_data = kw.pop('alt_limiter_data_array', None)

    # Get data
    if alt_lim_data is None and alt_lim_loc is None:
        return None
    elif alt_lim_data is None:
        alt_lim_data = eval(alt_lim_loc)
        lim_name = alt_lim_loc.split("'")[-2]
    else:
        lim_name = ''
    r = alt_lim_data[:, 0] * scale
    z = alt_lim_data[:, 1] * scale

    # Set up plot
    if ax is None:
        ax = scratch.get('efitviewer_cx_ax', None)
    if ax is None:
        ax = gca()
    kw.setdefault('label', 'Alternative limiter {}'.format(lim_name))

    return ax.plot(r, z, **kw)


# Plot and plot related utilities ---------------------------------------------------------------------------------
def plot_grid(fig=None, ax=None, enable=None, grid_kw=None):
    """
    :param fig: Figure instance

    :param ax: Axes instance

    :param enable: bool

    :param grid_kw: dict
        Keywords passed to grid
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    # Get default values
    if fig is None:
        fig = scratch.get('efitviewer_fig', None)
    if enable is None:
        enable = settings.setdefault('grid_enable', False)
    if grid_kw is None:
        grid_kw = settings.setdefault('grid_kw', {})
    ax = get_axes(ax)

    # Update grid
    if enable:
        ax.grid(enable, which='major', axis='both', **grid_kw)
    else:
        ax.grid(False, which='major', axis='both')

    # Make sure the update is actually drawn
    if fig is not None:
        fig.canvas.draw()
    return


def setup_special_contours(case=0, t=None, contour_quantity=None, spacing=None, decimal_places=3):
    """
    Finds contour levels in contour_quantity to give contours that obey settings in the dictionary called spacing

    :param case: int
        Which efitviewer case / ODS instance should be selected?

    :param t: float
        Time in s, to select a time slice in equilibrium data
        Defaults to setting for the relevant case in efitviewer settings

    :param contour_quantity: string
        Quantity for output contour levels. Defaults to contour quantity in efitviewer settings.

    :param spacing: dict
        Spacing instructions; can contain:
            quantity: string
                R, psi, psi_n, S
            amount: float array
                in data units relevant to quantity
            reference: string
                Reference point.
                For flux measurements, the reference is always the boundary & this setting is ignored.
                For R, try outer_midplane. For S, try outer_lower_strike.

    :param decimal_places: int
        Round to this many decimal places
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if case == 0:
        ods = out['efitviewer_ods']
    else:
        ods = out['efitviewer_ods_{}'.format(case)]
    if t is None:
        t = settings['cases'][case]['time'] / 1000.0
    if contour_quantity is None:
        contour_quantity = settings['contour_quantity']
    if spacing is None:
        spacing = settings['special_contour_spacing']

    it = closestIndex(ods['equilibrium']['time'], t)
    eq_slice = ods['equilibrium']['time_slice'][it]

    eq_phi = eq_slice['profiles_1d']['phi']
    eq_psi = eq_slice['profiles_1d']['psi']
    eq_psi_n = np.linspace(0, 1, len(eq_psi))

    cr = eq_slice['profiles_2d'][0]['grid']['dim1']
    cz = eq_slice['profiles_2d'][0]['grid']['dim2']
    if contour_quantity in ['psi', 'PSI']:
        cq = eq_slice['profiles_2d'][0]['psi']
        cq1d = eq_psi
    elif contour_quantity.lower() in ['psin', 'psi_n', 'psi_norm']:
        psi_bdry = eq_slice['global_quantities']['psi_boundary']
        psi_axis = eq_slice['global_quantities']['psi_axis']
        cq = (eq_slice['profiles_2d'][0]['psi'] - psi_axis) / (psi_bdry - psi_axis)
        cq1d = eq_psi_n
    elif contour_quantity in ['phi', 'PHI']:
        cq = eq_slice['profiles_2d'][0]['phi']
        cq1d = eq_phi
    else:
        raise ValueError('Contour quantity {} is not yet supported for this operation, sorry.'.format(contour_quantity))

    space_q = spacing.get('quantity', 'R')
    space_a = np.atleast_1d(spacing.get('amount', np.array([0, 0.01])))
    space_ref = spacing.get('reference', 'outer_midplane')
    if space_q in ['R', 'Rmaj', 'R_major', 's', 'S']:
        if space_ref.lower() in ['outer_midplane', 'omp']:
            rmaxis = eq_slice['global_quantities.magnetic_axis.r']
            zmaxis = eq_slice['global_quantities.magnetic_axis.z']
            bdry_r = eq_slice['boundary.outline.r']
            bdry_z = eq_slice['boundary.outline.z']
            wr = bdry_r > rmaxis
            r_omp = interp1d(bdry_z[wr], bdry_r[wr])(zmaxis)
            ref_r = r_omp
            ref_z = zmaxis
        elif space_ref.lower() in ['outer_lower_strike']:
            # omfit_omas.multi_efit_to_omas() loads strike points in a set order: low out, low in, up out, up in
            try:
                ref_r = eq_slice['boundary.strike_point.0.r']
                ref_z = eq_slice['boundary.strike_point.0.z']
            except ValueError:
                ref_r = ref_z = np.NaN
            if np.isnan(ref_r) or np.isnan(ref_z):
                raise ValueError('Outer lower strike point not defined; might be a limited or upper-biased shape or just missing from ODS')
        elif space_ref.lower() in ['outer_upper_strike']:
            # omfit_omas.multi_efit_to_omas() loads strike points in a set order: low out, low in, up out, up in
            ref_r = eq_slice['boundary.strike_point.2.r']
            ref_z = eq_slice['boundary.strike_point.2.z']
            if np.isnan(ref_r) or np.isnan(ref_z):
                raise ValueError('Outer upper strike point not defined; might be a limited or lower-biased shape or just missing from ODS')
        else:
            raise ValueError('Unrecognized custom contour spacing reference: {}'.format(space_ref))
        if space_q in ['R', 'Rmaj', 'R_major']:
            dr = space_a
            r = ref_r + dr
            z = ref_z + dr * 0
        elif space_q in ['S', 's']:
            ds = space_a
            wallr0 = ods['wall.description_2d.0.limiter.unit.0.outline.r']
            wallz0 = ods['wall.description_2d.0.limiter.unit.0.outline.z']
            # Upsample the wall so that the nearest point will be on the right surface. Since the wall has detailed
            # features, the nearest point can be behind the true surface. For example, a strike point on the lower
            # shelf might find a closest wall point in the pump duct under the shelf. To avoid locking onto such a
            # point, put in lots of extra points along the wall contour instead.
            idx = np.linspace(0, 1, len(wallr0))
            new_idx = np.linspace(0, 1, 20 * len(wallr0))
            wallr = interp1d(idx, wallr0)(new_idx)
            wallz = interp1d(idx, wallz0)(new_idx)
            ref_dist = np.sqrt((wallr - ref_r) ** 2 + (wallz - ref_z) ** 2)
            ic = ref_dist.argmin()

            # Figure out which way the wall goes
            neighborhood = np.arange(ic - 3, ic + 3)
            neighborhood = neighborhood[(neighborhood >= 0) & (neighborhood < len(wallr))]
            if np.nanmean(np.diff(wallr[neighborhood])) > 0:
                wall_dir = 1
            else:
                wall_dir = -1

            # Get wall coordinate
            wall_ds = np.append(0, np.sqrt(np.diff(wallr) ** 2 + np.diff(wallz) ** 2))
            wall_s = np.cumsum(wall_ds) * wall_dir
            wall_s -= wall_s[ic]

            # Get s coordinates of requested contour levels
            if ref_r > wallr[ic]:
                ref_s = ref_dist[ic]
            else:
                ref_s = -ref_dist[ic]
            s = ref_s + ds
            # Get R-Z coordinates of requested contour levels
            r = interp1d(wall_s, wallr)(s)
            z = interp1d(wall_s, wallz)(s)

        else:
            raise ValueError
        # Translate R-Z coordinates into flux surface labels (like psi, etc)
        contour_levels = (interp2d(cr, cz, cq.T, bounds_error=False, fill_value=np.NaN)(r, z))[0]
    elif space_q.lower() == 'psi':
        psi_levels = eq_slice['global_quantities']['psi_boundary'] + space_a
        contour_levels = interp1d(eq_psi, cq1d)(psi_levels)
    elif space_q.lower() in ['psi_n', 'psin']:
        psin_levels = 1 + space_a
        contour_levels = interp1d(eq_psi_n, cq1d)(psin_levels)
    else:
        raise ValueError('Unrecognized quantity for spacing contours: {}'.format(space_q))

    return np.round(contour_levels, decimal_places)


def get_axes(ax=None, which='cx'):
    """
    Choose the best plot axes to use

    :param ax: Axes instance or 2D array of Axes instances [optional]
        If not specified, try to use efitviewer GUI's embedded axes. If those are not active, use gca().

    :param which: str
        cx: deal with cross section axes
        profile: deal with array of profile axes

    :return: Axes instance or 2D array of Axes instances
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    if which == 'cx' and not settings.get('show_cx', True):
        printd(f'show_cx is off, so no cx_ax is needed. Returning None...', topic='efitviewer')
        return None
    if which == 'profile' and settings.get('profiles', {}).get('num_profiles', 0) < 1:
        printd(f'num_profiles < 1, so no profile_axes are needed. Returning None...', topic='efitviewer')

    if ax is None:
        printd(f'plot_single_cx_ods(): trying to look up efitviewer axes for {which}...', topic='efitviewer')
        if which == 'profile':
            ax = scratch.get('efitviewer_profile_axs', None)
            if ax is not None and len(ax.flatten()):
                test_ax = ax[0, 0]
            else:
                test_ax = None
        else:
            ax = scratch.get('efitviewer_cx_ax', None)
            test_ax = ax
    else:
        printd(f'received some axes to check against the needs of {which}...', topic='efitviewer')
        test_ax = ax
        if which == 'profile':
            if len(test_ax.flatten()):
                test_ax = ax[0, 0]
            else:
                test_ax = None
    if test_ax is not None:
        printd(f'testing whether {which} axes have a figure associated with them', topic='efitviewer')
        # Check if ax is active
        try:
            # https://stackoverflow.com/a/15311949/6605826
            tk_figure_open = test_ax.figure.canvas.get_tk_widget().winfo_exists()
        except Exception:
            # I assume that get_tk_widget() will fail if the backend isn't tk
            tk_figure_open = False
        # https://stackoverflow.com/a/26485683/6605826
        figure_window_open = test_ax.figure in list(map(pyplot.figure, pyplot.get_fignums()))

        if (not tk_figure_open) and (not figure_window_open):
            printd('plot_single_cx_ods(): efitviewer figure seems to have been closed', topic='efitviewer')
            ax = None
    if ax is None:
        printd('plot_single_cx_ods(): using populate_efitviewer_figure()', topic='efitviewer')
        fig = scratch['efitviewer_fig'] = pyplot.figure()
        settings.setdefault('profiles', SettingsName())
        cx_ax, profile_axs = populate_efitviewer_figure(
            fig,
            scratch,
            show_cx=settings.setdefault('show_cx', True),
            num_profiles=settings['profiles'].setdefault('num_profiles', 0),
            num_profile_cols=settings['profiles'].setdefault('num_profile_cols', 0),
            profiles_sharex=settings['profiles'].setdefault('sharex', 'all'),
            profiles_sharey=settings['profiles'].setdefault('sharey', 'none'),
            **settings['profiles'].setdefault('gridspec_kw', {}),
        )
        if which == 'profile':
            ax = profile_axs
        else:
            ax = cx_ax

    return ax


def save_subplot_layout(reset=False):
    """
    Either saves the current layout of subplots in the efitviewer figure, or erases prior records of fig layout

    The saves are particular to each configuration (number of columns, CX on/off, number of profile plots).

    :param reset: bool
        Erase the last record instead of saving
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    show_cx = settings.get('show_cx', True)
    ncol = settings.get('profiles', {}).get('num_profile_cols', 0)
    if ncol == 0:
        ncol = 1
    tag = f'{"cx" if show_cx else ""}-{ncol}-{settings.get("profiles", {}).get("num_profiles", 0)}'
    if reset:
        settings['plot_style_kw'].setdefault('subplot_layout', SettingsName()).pop(tag, None)
        return
    layout = settings['plot_style_kw'].setdefault('subplot_layout', SettingsName()).setdefault(tag, SettingsName())
    fig = scratch['efitviewer_fig']
    for attr in ['wspace', 'hspace', 'left', 'right', 'bottom', 'top']:
        layout[attr] = getattr(fig.subplotpars, attr, None)


def plot_style_enforcement(ax=None, plot_style=None):
    """
    Applies efitviewers plot style settings to some axes

    :param ax: Axes instance [optional]
        Axes to modify; looks up efitviewer GUI axes or gca() if not specified

    :param plot_style: dict-like [optional]
        Settings to use for modifying axes appearance
    """
    # Unpack settings and axes reference
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    if plot_style is None:
        plot_style = settings.get('plot_style_kw', {})
    ax = get_axes(ax)
    if ax is None:
        return
    fig = ax.figure

    # Frame
    frame_on = plot_style.setdefault('frame_on', True)
    if frame_on is not None:
        ax.set_frame_on(frame_on)

    # Aspect ratio
    aspect = plot_style.setdefault('axes_aspect', 'equal_box')
    if aspect is not None:
        if '_' in str(aspect):
            aspect_ratio, adjustable = aspect.split('_')
        elif is_numeric(aspect):
            aspect_ratio = aspect
            adjustable = None
        else:
            aspect_ratio = aspect
            adjustable = None
        ax.set_aspect(aspect_ratio, adjustable=adjustable)

    # Tick spacing
    if plot_style.setdefault('tick_spacing', 0.25) is not None:
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(plot_style['tick_spacing']))
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(plot_style['tick_spacing']))

    # Tick position
    ax.xaxis.set_ticks_position(plot_style.setdefault('xtick_loc', 'both'))
    ax.yaxis.set_ticks_position(plot_style.setdefault('ytick_loc', 'both'))

    # Grid
    plot_grid(fig=fig, ax=ax, enable=plot_style.setdefault('grid_enable', False), grid_kw=plot_style.setdefault('grid_kw', {}))

    # Subplots layout
    show_cx = settings.get('show_cx', True)
    ncol = settings.get('profiles', {}).get('num_profile_cols', 0)
    if ncol == 0:
        ncol = 1
    tag = f'{"cx" if show_cx else ""}-{ncol}-{settings.get("profiles", {}).get("num_profiles", 0)}'
    layout = settings['plot_style_kw'].setdefault('subplot_layout', SettingsName()).setdefault(tag, SettingsName())
    fig.subplots_adjust(**layout)

    # Annotations
    if plot_style.setdefault('subplot_label', None) is not None:
        font_size = settings.get('default_fontsize', None)
        if font_size is None:
            font_size = matplotlib.rcParams['xtick.labelsize']
        tag_plots_abc(
            fig=fig,
            axes=ax,
            start_at=plot_style.setdefault('subplot_label', 0),
            corner=plot_style.setdefault('subplot_label_corner', [1, 1]),
            font_size=font_size,
        )
    return


# Main plotting functions -----------------------------------------------------------------------------------------
def populate_efitviewer_figure(
    fig, scratch, show_cx=True, num_profiles=0, num_profile_cols=0, profiles_sharex='all', profiles_sharey='none', **gridspec_kw
):
    """
    Adds subplots to the efitviewer figure

    :param fig: Figure instance
        Can be a standalone matplotlib figure, or an OMFITx.Figure GUI element

    :param scratch: dict-like
        Scratch space

    :param show_cx: bool
        Show the cross section subplot (otherwise just profiles are shown)

    :param num_profiles: int
        Number of panels for profile plots

    :param num_profile_cols: int
        Number of columns for profiles

    :param profiles_sharex: str
        Share the x axis between profiles. Options: 'none', 'all', 'row', 'col'.

    :param profiles_sharey: str
        Share the Y axis between profiles. Options: 'none', 'all', 'row', 'col'.

    :param gridspec_kw: keywords to pass to gridspec.
        width_ratios is especially useful; use it to set the relative widths of
        columns by passing a numeric iterable matching the total number of
        columns (including CX, if shown)

    :return: tuple
        Axes instance: axes for the cross section or None if not used
        2D array of Axes instances, padded with None as needed: axes for the profiles
            Padding with None would be needed for cases like 8 plots in a 3x3 arrangement,
            where one panel would be blank.
    """
    # Set up the grid
    if num_profiles > 0:
        num_profile_cols_ = np.min([np.max([1, num_profile_cols]), num_profiles])
        num_rows = int(np.max([np.ceil(num_profiles / float(num_profile_cols_)), 1]))
    else:
        num_profile_cols_ = 0
        num_rows = 1
    try:
        gs = matplotlib.gridspec.GridSpec(num_rows, num_profile_cols_ + show_cx, **gridspec_kw)
    except Exception:
        gs = matplotlib.gridspec.GridSpec(num_rows, num_profile_cols_ + show_cx)
        report = ''.join(traceback.format_exception(*sys.exc_info()))
        printe('Gridspec keywords for setting up efitviewer profile plots were invalid and were ignored!')
        print(report)
        printe('Gridspec keywords for setting up efitviewer profile plots were invalid and were ignored!')

    if show_cx:
        cx_ax = scratch['efitviewer_cx_ax'] = fig.add_subplot(gs[:, 0])
    else:
        cx_ax = scratch['efitviewer_cx_ax'] = None

    profile_axs = scratch['efitviewer_profile_axs'] = np.empty((num_rows, num_profile_cols_), dtype=object)
    for i in range(num_rows):
        for j in range(num_profile_cols_):
            profile_axs[i, j] = None

    for i in range(num_profiles):
        row = i % num_rows
        col = i // num_rows
        fig_col = col + show_cx
        if (i > 0) and profiles_sharex != 'none':
            if profiles_sharex == 'all':
                sharex = profile_axs[0, 0]
            elif profiles_sharex == 'row':
                sharex = profile_axs[row, 0]
            elif profiles_sharex == 'col':
                sharex = profile_axs[0, col]
        else:
            sharex = None
        if (i > 0) and profiles_sharey != 'none':
            if profiles_sharey == 'all':
                sharey = profile_axs[0, 0]
            elif profiles_sharey == 'row':
                sharey = profile_axs[row, 0]
            elif profiles_sharey == 'col':
                sharey = profile_axs[0, col]
        else:
            sharey = None
        profile_axs[row, col] = fig.add_subplot(gs[row, fig_col], sharex=sharex, sharey=sharey)
        if (row < (num_rows - 1)) and (profiles_sharex in ['col', 'all']):
            profile_axs[row, col].get_xaxis().set_visible(False)
        if (col > 0) and profiles_sharey in ['row', 'all']:
            profile_axs[row, col].get_yaxis().set_visible(False)
    return cx_ax, profile_axs


def plot_cx_ods(ods_idx=None, odss=None, cases=None, **kw):
    r"""
    Wrapper for making multiple calls to plot_single_cx_ods()

    Note that plot_single_cx_ods() calls plot_single_time_profile_set(),
    so this is the umbrella for all CX and profile plots.

    :param ods_idx: int or list of ints [optional]
        You should probably let it do its default behavior, but you can override it if you need to.

    :param odss: dict [optional]
        Keys are int matching entries in ods_idx
        Values are ODS instances.
        This is for overriding ODSs in the tree to support some very specific operations and is
        not recommended for most purposes.

    :param cases: dict-like [optional]
        Dictionary with entries foe each index in ods_idx specifying time (float or float array) and active (bool)

    :param \**kw: Additional keywords passed to plot_single_cx_ods() for 0th case.
        See docstring for plot_single_cx_ods.
        If you have overridden ods with your own list, the first entry in the list gets all the keywords, and
        subsequent entries get a subset.

    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    printd('started plot_cx_ods...', topic='efitviewer')

    if cases is None:
        cases = settings['cases']
    if ods_idx is None:
        # Default automatic selection of ods indices to loop over
        ods_idx = []
        for idx in cases:
            # Collect indices of active cases to overlay
            if cases[idx].get('active', True) or idx == 0:
                ods_idx += [idx]
    if odss is None:
        odss = {k: None for k in ods_idx}

    tkw = kw.pop('t', None)
    first_only = ['overlays', 'special_overlays', 'customization']
    clear_first = kw.pop('clear_first', None)
    kw2 = copy.copy(kw)
    for fkw in first_only:
        kw2.pop(fkw, None)
    kw2['overlays'] = {}
    kw2['special_overlays'] = {}

    for i, idx in enumerate(tolist(ods_idx)):
        # Special call for the primary ODS
        printd('plot_single_cx_odx() call for equilibrium slice i={}, idx={}'.format(i, idx))
        if len(tolist(ods_idx)) <= 1:
            use_kw = kw
            printd('  allowing overlay instructions in this call instead of doing separately at the end')
        else:
            use_kw = kw2
            printd('  no overlay instructions yet; must repeat at the end')
        plot_single_cx_ods(
            ods_idx=idx,
            ods=odss[idx],
            multi_cases=len(tolist(ods_idx)) > 1,
            t=cases[idx].get('time', None) if tkw is None else tkw,
            eq_active=cases[idx].get('active', True),
            wall_active=cases[idx].get('wall', True),
            clear_first=clear_first and (i == 0),
            eqkw=cases[idx].get('eqkw', {}),
            xkw=cases[idx].get('xkw', dict(marker='x')),
            **use_kw,
        )
    if len(tolist(ods_idx)) > 1:
        # Diagnostic overlays from first ODS
        printd('  extra overlay call at the end for diagnostics')
        plot_single_cx_ods(
            ods_idx=0,
            ods=odss[0],
            multi_cases=len(tolist(ods_idx)) > 1,
            t=cases[0].get('time', None) if tkw is None else tkw,
            eq_active=False,
            wall_active=False,
            **kw,
        )
    return


def calc_btor_2d(ods, t_idx):
    """
    Calculates the toroidal magnetic field on the 2D grid

    :param ods: ODS instance

    :param t_idx: int
    """
    s = ods['equilibrium.time_slice'][t_idx]
    t = ods['equilibrium.time']
    bcentr = interp1d(t, ods['equilibrium.vacuum_toroidal_field.b0'])(s['time'])
    rcentr = ods['equilibrium.vacuum_toroidal_field.r0']
    rgrid = s['profiles_2d.0.grid.dim1']
    zgrid = s['profiles_2d.0.grid.dim2']
    btvac = bcentr * rcentr / rgrid
    btvac2d = btvac[:, np.newaxis] + zgrid[np.newaxis, :] * 0

    psi1d = s['profiles_1d.psi']
    f1d = s['profiles_1d.f']
    psi2d = s['profiles_2d.0.psi']
    f2d = interp1d(psi1d, f1d, bounds_error=False, fill_value=np.NaN)(psi2d)
    btor = f2d / rgrid[:, np.newaxis]
    btor[np.isnan(btor)] = btvac2d[np.isnan(btor)]
    s['profiles_2d.0.b_field_tor'] = btor


def calculate_j_toroidal(ods, t_idx, check_availability=False):
    """
    Calculates toroidal current density

    :param ods: ODS instance

    :param t_idx: int

    :param check_availability: bool
        Return a bool flag indicating whether the calculation is possible instead of doing the calculation

    :return: 1D float array
    """
    from omfit_classes.fluxSurface import fluxSurfaces

    scratch = pick_output_location()[5]

    profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
    profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
    global_quantities = ods['equilibrium.time_slice'][t_idx]['global_quantities']
    required_2d = ['psi']
    required_1d = ['psi', 'f']
    required_global = ['magnetic_axis.r']

    is_available = all(
        [r in profiles_1d for r in required_1d]
        + [r in profiles_2d for r in required_2d]
        + [r in global_quantities for r in required_global]
    )
    if check_availability:
        return is_available

    if (profiles_1d.get('r_outboard', None) is None) or (not len(profiles_1d['r_outboard'])) or np.all(np.isnan(profiles_1d['r_outboard'])):
        define_r_outboard(ods, t_idx)
    if (
        (profiles_2d.get('b_field_tor', None) is None)
        or (not len(profiles_2d['b_field_tor']))
        or np.all(np.isnan(profiles_2d['b_field_tor']))
    ):
        calc_btor_2d(ods, t_idx)

    fluxtag = f"flux_surfaces_{ods['dataset_description.data_entry.machine']}#{ods['dataset_description.data_entry.pulse']}_{t_idx}"
    fluxsurf = scratch[fluxtag] = fluxSurfaces(
        Rin=profiles_2d['grid.dim1'],
        Zin=profiles_2d['grid.dim2'],
        PSIin=profiles_2d['psi'].T,
        Btin=profiles_2d['b_field_tor'].T,
        Rcenter=global_quantities['magnetic_axis.r'],
        F=profiles_1d['f'],
        P=profiles_1d['pressure'],
        rlim=ods['wall.description_2d.0.limiter.unit.0.outline.r'],
        zlim=ods['wall.description_2d.0.limiter.unit.0.outline.z'],
        levels=np.linspace(0, 1, len(profiles_1d['psi'])),
        gEQDSK=None,
        cocosin=ods.cocos,
    )
    profiles_1d['j_tor'] = fluxsurf['avg']['Jt']


def define_r_outboard(ods, t_idx=None):
    """
    Given an ODS with an equilibrium, define the 1D profile quantity r_outboard is defined.

    :param ods: ODS instance

    :param t_idx: int
        Index of the time slice to work on
    """
    profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
    profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
    global_quantities = ods['equilibrium.time_slice'][t_idx]['global_quantities']
    r = profiles_2d['grid.dim1']
    z = profiles_2d['grid.dim2']
    psi2d = profiles_2d['psi']
    rmaxis = global_quantities['magnetic_axis.r']
    zmaxis = global_quantities['magnetic_axis.z']
    zidx = abs(z - zmaxis).argmin()
    rsel = r >= rmaxis
    psi_omp = psi2d[rsel, zidx]
    r_slice = r[rsel]
    profiles_1d['r_outboard'] = interp1d(psi_omp, r_slice, bounds_error=False, fill_value='extrapolate')(profiles_1d['psi'])


def take_slice_of_2d(quantity, ods, t_idx):
    """
    Takes a 1D slice out of a 2D profile quantity

    :param quantity: str

    :param ods: ODS instance

    :param t_idx: int

    :return: 1D float array
    """
    profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
    profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
    global_quantities = ods['equilibrium.time_slice'][t_idx]['global_quantities']
    if (profiles_1d.get('r_outboard', None) is None) or (not len(profiles_1d['r_outboard'])) or np.all(np.isnan(profiles_1d['r_outboard'])):
        define_r_outboard(ods, t_idx)
    rtar = profiles_1d['r_outboard']
    ztar = global_quantities['magnetic_axis.z'] + 0 * rtar
    return RectBivariateSpline(profiles_2d['grid.dim1'], profiles_2d['grid.dim2'], profiles_2d[quantity])(rtar, ztar, grid=False)


def get_quantity(quantity, ods, t_idx):
    """
    Intercept quantity request to calculate special quantities as needed

    :param quantity: str

    :param ods: ODS instance

    :param t_idx: int

    :return: 1D float array
    """
    profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
    profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
    global_quantities = ods['equilibrium.time_slice'][t_idx]['global_quantities']
    if quantity == 'b_field_tor' and quantity not in profiles_2d:
        calc_btor_2d(ods, t_idx)
    if quantity == 'j_tor' and quantity not in profiles_1d and calculate_j_toroidal(ods, t_idx, check_availability=True):
        calculate_j_toroidal(ods, t_idx)
    if quantity == 'psi_norm':
        q = (profiles_1d['psi'] - global_quantities['psi_axis']) / (global_quantities['psi_boundary'] - global_quantities['psi_axis'])
    elif (quantity not in profiles_1d) and (quantity in profiles_2d):
        q = take_slice_of_2d(quantity, ods, t_idx)
    else:
        q = profiles_1d[quantity]
    return q


def constraint_profile_mse_polarisation_angle(ods, t_idx=0, profile_x_quantity='R', ax=None, **plot_kw):
    """
    Plots a profile of the MSE polarization angle constraint

    Each constraint profile plot function must accept these keywords: [ods, t_idx, profile_x_quantity, ax]
    Each constraint profile plot function must be named exactly:
        'constraint_profile_{name of constraint set in equilibrium}'

    :param ods: ODS instance

    :param t_idx: int

    :param profile_x_quantity: str

    :param ax: Axes instance

    :param plot_kw: Addtional keywords passed to plot and errorbar
    """
    if ax is None:
        # Only relevant for testing; otherwise a specific set of Axes within the
        # profile axes set should always be provided by the calling function.
        ax = gca()
    mse_eq = ods['equilibrium.time_slice'][t_idx]['constraints.mse_polarisation_angle']
    nchan = len(mse_eq)
    r = np.empty(nchan)
    z = np.empty(nchan)
    measured = np.empty(nchan)
    measured_err = np.empty(nchan)
    reconstructed = np.empty(nchan)
    for ch in range(nchan):
        r[ch] = ods[mse_eq[ch]['source']]['active_spatial_resolution.0.centre.r']
        z[ch] = ods[mse_eq[ch]['source']]['active_spatial_resolution.0.centre.z']
        measured[ch] = mse_eq[ch]['measured']
        measured_err[ch] = mse_eq[ch]['measured_error_upper']
        reconstructed[ch] = mse_eq[ch]['reconstructed']

    if profile_x_quantity.lower() == 'r':
        x = r
        ax.set_xlabel('R / m')
    elif profile_x_quantity.lower() == 'z':
        x = z
        ax.set_xlabel('Z / m')
    else:
        profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
        profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
        psi = RectBivariateSpline(profiles_2d['grid.dim1'], profiles_2d['grid.dim2'], profiles_2d['psi'])(r, z, grid=False)
        x = interp1d(profiles_1d['psi'], get_quantity(profile_x_quantity, ods, t_idx), bounds_error=False, fill_value=np.NaN)(psi)
        ax.set_xlabel(omas_eq1d_pretty_name(profile_x_quantity))

    ax.set_ylabel('MSE pitch angle / radians')

    pkw = copy.deepcopy(plot_kw)
    for naughty in ['linestyle', 'marker', 'ls', 'label']:
        pkw.pop(naughty, None)

    a = ax.errorbar(x, measured, measured_err, marker='x', linestyle='', label='Measured', **pkw)
    # Don't use the next color in the cycle or else these profile colors won't line up with equilibrium colors
    pkw['color'] = associated_color(a[0].get_color())
    ax.plot(x, reconstructed, marker='.', linestyle='', label='Reconstructed', **pkw)
    ax.legend(loc=0)


def plot_single_time_profile_set(
    ods=None, t_idx=0, profile_axs=None, profile_x_quantity=None, profile_y_quantities=None, gentle=False, **plotkw
):
    """
    Plots profiles for a single time-slice

    This is normally called by plot_single_cx_ods()

    :param ods: ODS() instance with the data

    :param t_idx: int

    :param profile_axs: 2D array of Axes instances

    :param profile_x_quantity: str

    :param profile_y_quantities: list of strings

    :param gentle: bool
        Report exceptions with print and ax.text instead of raising

    :param plotkw: Additional keywords passed to plot and plot-related functions in constraint profiles
        Could be passed to errorbar(), for example.
    """
    if profile_axs is None or profile_x_quantity is None:
        return
    settings = pick_output_location()[3]

    profiles_1d = ods['equilibrium']['time_slice'][t_idx]['profiles_1d']
    profiles_2d = ods['equilibrium']['time_slice'][t_idx]['profiles_2d'][0]
    constraints = ods['equilibrium']['time_slice'][t_idx]['constraints']
    global_quantities = ods['equilibrium.time_slice'][t_idx]['global_quantities']

    if (profile_x_quantity == 'r_outboard') and ('r_outboard' not in profiles_1d):
        define_r_outboard(ods, t_idx)

    # Sanitize plotkw
    pkw = copy.deepcopy(plotkw)
    for naughty in ['linewidths', 'colors', 'linestyles']:
        pkw.pop(naughty, None)

    for i, ax in enumerate(profile_axs.flatten()):
        if profile_y_quantities[i] is None:
            return

        # Is it a constraint that needs a special function?
        if (
            (profile_y_quantities[i] not in profiles_1d)
            and (profile_y_quantities[i] not in profiles_2d)
            and (profile_y_quantities[i] in constraints)
        ):
            constraint_profile_function_name = f'constraint_profile_{profile_y_quantities[i]}'
        else:
            constraint_profile_function_name = None

        if constraint_profile_function_name is None:
            ax.set_xlabel(omas_eq1d_pretty_name(profile_x_quantity))
            ax.set_ylabel(omas_eq1d_pretty_name(profile_y_quantities[i]))
        try:
            if constraint_profile_function_name is not None:
                constraint_profile_function = eval(constraint_profile_function_name)
                constraint_profile_function(ods=ods, t_idx=t_idx, profile_x_quantity=profile_x_quantity, ax=ax, **pkw)
            else:
                ax.plot(get_quantity(profile_x_quantity, ods, t_idx), get_quantity(profile_y_quantities[i], ods, t_idx), **pkw)
        except (KeyError, ValueError, NameError):
            if gentle:
                # Display the error instead of bringing the whole GUI down if the plot fails.
                print('Error in plot_single_time_profile_set:')
                report = ''.join(traceback.format_exception(*sys.exc_info()))
                printe(report)
                # noinspection PyBroadException
                try:
                    ax.text(0.05, 0.95, report, ha='left', va='top', color='red')
                except Exception:
                    printd('plot_single_cx_ods{}: Failed to properly report an exception!', topic='efitviewer')
            else:
                raise

    if settings['profiles'].get('sharex', 'all') in ['all', 'col']:
        if len(profile_axs[:, 0]) > 1:
            for ax in profile_axs[:-1, :].flatten():
                ax.set_xlabel('')
    if settings['profiles'].get('sharey', 'none') in ['all', 'row']:
        if len(profile_axs[0, :]) > 1:
            for ax in profile_axs[:, 1:].flatten():
                ax.set_ylabel('')

    if len(np.shape(profile_axs)) > 1 and np.shape(profile_axs)[1] > 1 and settings['profiles'].setdefault('last_col_right_label', True):
        for ax in profile_axs[:, -1].flatten():
            ax.yaxis.tick_right()
            ax.yaxis.set_ticks_position('both')
            ax.yaxis.set_label_position("right")


def plot_single_cx_ods(
    cx_ax=None,
    profile_axs=None,
    ods_idx=0,
    multi_cases=False,
    ods=None,
    t=None,
    overlays=None,
    special_overlays=None,
    clear_first=False,
    gentle=False,
    contour_quantity=None,
    allow_fallback=None,
    levels=None,
    contour_resample_factor=None,
    xlim=None,
    ylim=None,
    customization=None,
    default_fontsize=None,
    show_legend=None,
    show_cornernote=None,
    eq_active=None,
    wall_active=None,
    profile_x_quantity=None,
    profile_y_quantities=None,
    plot_style_kw=None,
    eqkw=None,
    xkw=None,
):
    """
    Plots efitviewer-style cross section with overlays

    If data for an overlay are missing, they will be added before plotting.

    This function also calls plot_single_time_profile_set() to add profiles to the figure.

    :param cx_ax: Axes instance
        Axes to draw cross section on.

    :param profile_axs: 2D array containing Axes instances
        Axes to use for drawing profiles.
        Profiles disabled if set to None
        Pad with None if necessary (e.g. 8 plots in a 3x3 arrangement with one missing).

    :param ods_idx: int
        For looking up which group of settings to use, & for looking up which ODS to use, if ods is not overridden.

    :param multi_cases: bool
        Set up for supporting multi-case overlay. Affects how some annotations are drawn.
        Does not actually do multiple cases in this call.

    :param ods: ODS instance
        This is the source of data. At minimum, it should contain equilibrium data for plotting contours.

    :param t: numeric scalar or iterable
        Time slice(s) of interest (ms). Control multi-slice overlays by passing a list or array.

    :param overlays: dict
        Dictionary with keys matching standard hardware systems and bool keys to activate overlays of those systems

    :param special_overlays: dict
        Dictionary with keys matching special hardware overlays
        Each function should accept ax, ods, t, and value

    :param clear_first: bool
        Clears Axes before plotting. Use for quickly updating the same plot embedded in a GUI.

    :param gentle: bool
        Prints exception reports instead of raising exceptions.
        Use to prevent a whole GUI system from going down on a failed plot.

    :param contour_quantity: string
        Options: psi (poloidal mag flux), rho (sqrt of toroidal mag flux), or phi (toroidal mag flux)

    :param allow_fallback: bool
        If rho/psi/phi isn't available, allow fallback to something that is

    :param levels: numeric iterable
        Contour levels

    :param contour_resample_factor: int
        Upsample 2d data to improve contour smoothness

    :param xlim: two element sorted numeric iterable

    :param ylim: two element sorted numeric iterable

    :param customization: dict-like
        Each key should match the name of an overlay, like 'scaled_boundary' or 'gas_injection'.
        The values should be dict-like and contain keywords and values to pass to the overlay
        functions. Some of these keywords have been standardized, but others are specific
        to individual plot overlay functions. The GUI will interpret function docstrings
        to provide entries for setting these up properly.

    :param default_fontsize: float

    :param show_legend: int
        0: prevent legend, even if it's a good idea
        1: do legend even if other annotations could probably cover it
        2: auto select: do legend for multi-cases only

    :param show_cornernote: int
        0: prevent cornernote, even if it's a good idea
        1: do cornernote based on primary case even if it might be not be the best idea
            (like if it mismatches with other cases that are also shown)
        2: auto select: do cornernote for single case only

    :param eq_active: bool
        Equilibrium overlay active?

    :param wall_active: bool
        Wall overlay active / included in eq overlay?

    :param profile_x_quantity: str
        Quantity to use on the X-axes of the profile plots.

    :param profile_y_quantities: list of strings
        Quantities to show on the Y-axes of the profile plots. Must be at least as long as profile_axs.

    :param plot_style_kw: dict-like
        Settings for enforcing plot axes style

    :param eqkw: dict-like
        Customization options for equilibrium overlay contours and profile plots,
        passed to plot for boundary & contour for flux surfaces and to profiles.

    :param xkw: dict-like
        Customization options for equilibrium overlay's x-point, such as marker, color, markersize, mew, ...
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if ods is None:
        printd('plot_single_cx_ods(): no ODS passed; must try to look up...', topic='efitviewer')
        if ods_idx == 0:
            ods_tag = 'efitviewer_ods'
        else:
            ods_tag = 'efitviewer_ods_{}'.format(ods_idx)
        ods = out.get(ods_tag, None)
        printd('plot_single_cx_ods(): tried to get tag {} from {}'.format(ods_tag, out_loc), topic='efitviewer')
    else:
        printd('plot_single_cx_ods(): ODS was received; no auto-lookup', topic='efitviewer')
        ods_tag = None
    if ods is None:
        printd('plot_single_cx_ods(): ODS is still None after trying auto-lookup; aborting.', topic='efitviewer')
        return
    printd('plot_single_cx_ods(): ODS is okay now.', topic='efitviewer')

    timing_ref = None  # time.time()  # If this is not None, timing information will be printed
    if timing_ref is not None:
        printe('-' * 80)

    if clear_first and cx_ax is None and profile_axs is None:
        fig = scratch.setdefault('efitviewer_fig', None)
        if fig is None:
            fig = scratch['efitviewer_fig'] = pyplot.gcf()
        for ax in fig.axes:
            ax.remove()
        populate_efitviewer_figure(
            fig,
            scratch,
            show_cx=settings.setdefault('show_cx', True),
            num_profiles=settings['profiles'].setdefault('num_profiles', 0),
            num_profile_cols=settings['profiles'].setdefault('num_profile_cols', 0),
            profiles_sharex=settings['profiles'].setdefault('sharex', 'all'),
            profiles_sharey=settings['profiles'].setdefault('sharey', 'none'),
            **settings['profiles'].setdefault('gridspec_kw', {}),
        )

    cx_ax = get_axes(cx_ax)
    if isinstance(cx_ax, matplotlib.axes.Axes):
        fig = cx_ax.figure
    else:
        fig = None
    profile_axs = get_axes(profile_axs, which='profile')
    if fig is None and profile_axs is not None and isinstance(profile_axs[0, 0], matplotlib.axes.Axes):
        fig = profile_axs[0, 0].figure
    elif fig is None:
        fig = scratch.get('efitviewer_fig', None)
    if clear_first:
        if cx_ax is not None:
            cx_ax.cla()
        if profile_axs is not None:
            for ax in profile_axs.flatten():
                if ax is not None:
                    ax.cla()

    # noinspection PyBroadException
    try:
        if 'comment' in ods['dataset_description.ids_properties']:
            ids_comment = 'There is a comment in the ODS:\n' + ods['dataset_description.ids_properties.comment']
        else:
            ids_comment = ''
        if 'equilibrium' not in ods:
            raise EfitviewerDataError('No equilibrium data. Cannot plot.' + ids_comment)
        if 'time' not in ods['equilibrium']:
            raise EfitviewerDataError('No time in equilibrium; nothing to plot.' + ids_comment)

        # Resolve keyword default values
        if contour_quantity is None:
            contour_quantity = settings.setdefault('contour_quantity', 'psi_norm')
        if allow_fallback is None:
            allow_fallback = settings.setdefault('allow_fallback', False)
        if levels is None:
            levels = settings['{}_levels'.format(contour_quantity)]
        if contour_resample_factor is None:
            contour_resample_factor = settings['contour_resample_factor']
        if xlim is None:
            xlim = settings['xlim']
        if ylim is None:
            ylim = settings['ylim']
        if overlays is None:
            overlays = settings['systems']
        if special_overlays is None:
            special_overlays = settings['special_systems']
        if t is None:
            t = evalExpr(settings['cases'][ods_idx]['time'])
        if customization is None:
            customization = settings['co_efv']
        if default_fontsize is None:
            default_fontsize = settings.get('default_fontsize', None)
        if show_legend is None:
            show_legend = settings.setdefault('show_legend', 2)
        if show_cornernote is None:
            show_cornernote = settings.setdefault('show_cornernote', 2)
        if eq_active is None:
            eq_active = settings['cases'][ods_idx]['active']
        if wall_active is None:
            wall_active = settings['cases'][ods_idx].get('wall', True)
        settings.setdefault('profiles', SettingsName())
        if profile_x_quantity is None:
            profile_x_quantity = settings['profiles'].get('xaxis_quantity', None)
        if profile_y_quantities is None:
            profile_y_quantities = [settings['profiles'].get(f'yaxis_quantity_{i}', None) for i in range(len(profile_axs.flatten()))]
        if plot_style_kw is None:
            plot_style_kw = settings.setdefault('plot_style_kw', {})
        if eqkw is None:
            eqkw = settings['cases'][ods_idx].get('eqkw', {})
        if xkw is None:
            xkw = settings['cases'][ods_idx].get('xkw', {'marker': 'x'})

        if timing_ref is not None:
            print(time.time() - timing_ref, 'omfitlib efitviewer unpack stuff')

        # Get machine and shot info
        device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
        shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
        try:
            efitid = ods['dataset_description.ids_properties.comment'].split('EFIT tree = ')[-1]
        except ValueError:
            efitid = ''
        if t is None:
            printd('plot_single_cx_ods{}: t is None; aborting...', topic='efitviewer')
            return
        t = np.atleast_1d(t)

        printd('ods_idx', ods_idx, 'ods_tag', ods_tag, 't', t)

        # Gather overlay information as needed
        for overlay, overlay_active in overlays.items():
            printd(
                'checking overlay {}; active = {}, in ods = {}, in pulse_schedule: {}'.format(
                    overlay, overlay_active, overlay in ods, overlay in ods['pulse_schedule']
                )
            )
            if overlay_active and (overlay not in ods) and (overlay not in ods['pulse_schedule']):
                printd('  Need to add missing overlay data: {}'.format(overlay))
                add_hardware_to_ods(ods, device, shot, overlay)

        if timing_ref is not None:
            print(time.time() - timing_ref, 'omfitlib efitviewer add missing data')

        # Plot equilibrium time-slice(s)
        if eq_active:
            printd('plot_single_cx_ods{}: this eq slice is active; trying to plot', topic='efitviewer')
            it = None
            for t_ in t:
                if t_ is None:
                    it = 0
                else:
                    it = closestIndex(ods['equilibrium.time'] * 1000, t_)
                # Set up keywords for equilibrium_CX
                if multi_cases:
                    eqcx_label = 'eq#{}: {}#{} {} {:0.1f} ms'.format(ods_idx, device, shot, efitid, ods['equilibrium.time'][it] * 1000)
                else:
                    eqcx_label = 'Equilibrium {:0.1f} ms'.format(ods['equilibrium.time'][it] * 1000)
                eqcx_label = eqkw.pop('label', eqcx_label)
                eqcxkw = dict(
                    ax=cx_ax,
                    time_index=it,
                    levels=levels,
                    label=eqcx_label,
                    contour_quantity=contour_quantity,
                    allow_fallback=allow_fallback,
                    sf=contour_resample_factor,
                    xkw=xkw,
                    show_wall=(
                        (not special_overlays.get('alt_limiter', False)) or customization.get('alt_limiter', {}).get('retain_wall', True)
                    )
                    and wall_active,
                    **eqkw,
                )
                # Remove unsupported keywords based on omas version
                for kw, ver in omas_features.items():
                    if compare_version(ver, omas.__version__) > 0:
                        # Version required to support this keyword is newer than the OMAS version in use, so skip.
                        eqcxkw.pop(kw, None)
                if cx_ax is not None:
                    ods.plot_equilibrium_CX(**eqcxkw)  # The call to draw the equilibrium contours
                if profile_axs is not None:
                    plot_single_time_profile_set(
                        ods=ods,
                        t_idx=it,
                        profile_axs=profile_axs,
                        profile_x_quantity=profile_x_quantity,
                        profile_y_quantities=profile_y_quantities,
                        gentle=gentle,
                        **eqkw,
                    )
        elif cx_ax is not None:
            printd('plot_single_cx_ods{}: this eq slice is INACTIVE; skipping eq plot', topic='efitviewer')
            it = 0
            cx_ax.set_aspect('equal')
            cx_ax.set_frame_on(False)
            cx_ax.xaxis.set_ticks_position('bottom')
            cx_ax.yaxis.set_ticks_position('left')

        if cx_ax is not None:

            def overlay_customizations(ovls):
                ovls = dict(ovls)
                for ovl in ovls:
                    if ovls[ovl] and ovl in customization:
                        # Replace "True" w/ custom overlay instructions (if present) but first do some processing
                        custom = dict(customization[ovl])
                        for item in list(custom.keys()):
                            # Remove "None", since we were too busy to look up real defaults & they might not be None
                            if custom[item] is None:
                                if item == 't':
                                    custom[item] = t * 1e-3
                                else:
                                    custom.pop(item, None)
                            if item.startswith('pass_in_keywords_'):
                                pikw = custom.pop(item, {})
                                custom.update(pikw)
                        # Special debugging
                        if ovl in ['position_control', 'pulse_schedule']:
                            custom['timing_ref'] = timing_ref
                        # Custom instructions ready
                        if len(custom):
                            ovls[ovl] = custom
                        else:
                            ovls[ovl] = True
                return ovls

            # Plot hardware overlay(s)
            overlays = overlay_customizations(overlays)
            scratch['overlays'] = overlays
            old_font_size = copy.copy(rcParams['font.size'])
            if default_fontsize is not None:
                try:
                    rcParams['font.size'] = default_fontsize
                except ValueError as exc:
                    printe(f"Could not set rcParams['font.size'] = {repr(default_fontsize)} " f"(default_fontsize), because of {exc}")

            scratch['overlays'] = overlays
            # Thomson scattering has a different default than others, so we must make sure blank is replaced by False
            overlays.setdefault('thomson_scattering', False)
            ods.plot_overlay(ax=cx_ax, **overlays)  # The call to do the overlays

            # Plot special hardware overlay(s)
            special_overlays = overlay_customizations(special_overlays)
            scratch['special_overlays'] = special_overlays
            for so, soa in special_overlays.items():
                if soa:
                    skw = soa if isinstance(soa, dict) else {}
                    function_name = 'plot_{}_overlay'.format(so)
                    try:
                        special_function = eval(function_name)
                    except NameError:
                        printe('Unrecognized special overlay: {} has no function (expected {})'.format(so, function_name))
                    else:
                        special_function(ax=cx_ax, ods=ods, **skw)

            # Annotations and finishing touches
            actually_show_legend = (multi_cases and (show_legend > 0)) or (show_legend == 1)
            actually_show_cornernote = (not multi_cases and (show_cornernote > 0)) or (show_cornernote == 1)
            if actually_show_legend:
                cx_ax.legend(loc=0)
            if actually_show_cornernote:
                cornernote(
                    ax=cx_ax,
                    device=device,
                    shot='{} {}'.format(shot, efitid),
                    time='{:0.2f}'.format(ods['equilibrium.time'][it] * 1000) if len(t) == 1 else ' ',
                )
            if xlim is not None:
                cx_ax.set_xlim(xlim)
            if ylim is not None:
                cx_ax.set_ylim(ylim)
            if len(t) > 1:
                cx_ax.legend(loc=3)

            plot_style_enforcement(ax=cx_ax, plot_style=plot_style_kw)

        if default_fontsize is not None:
            rcParams['font.size'] = old_font_size

        # Make sure it draws
        if fig is not None:
            fig.canvas.draw()
        printd('plot_single_cx_ods{}: finished plot attempts with no exceptions to catch', topic='efitviewer')

    except Exception:
        printd('plot_single_cx_ods{}: exception while trying to plot...', topic='efitviewer')
        if gentle:
            # Display the error instead of bringing the whole GUI down if the plot fails.
            print('Error in plot_cx:')
            report = ''.join(traceback.format_exception(*sys.exc_info()))
            printe(report)
            # noinspection PyBroadException
            try:
                if cx_ax is None:
                    cx_ax = gca()
                if clear_first:
                    cx_ax.cla()
                cx_ax.text(0.05, 0.95, report, ha='left', va='top', color='red')
            except Exception:
                printd('plot_single_cx_ods{}: Failed to properly report an exception!', topic='efitviewer')
        else:
            raise

    return


# Export ----------------------------------------------------------------------------------------------------------
def dump_plot_command_content():
    """
    Writes the contents of a script for reproducing the equilibrium cross section plot based on current settings

    :return: string
        Source code for a script that will reproduce the plot
    """

    import getpass
    import socket

    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    ods = out['efitviewer_ods']
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
    case_defaults = dict(time=0, active=True, wall=True, eqkw={}, xkw=dict(marker='x'))
    cases = {k: {kk: v.get(kk, case_defaults.get(kk, None)) for kk in v} for k, v in settings['cases'].items()}

    overlays = {k: v for k, v in settings['systems'].items() if v}
    special_overlays = {k: v for k, v in settings['special_systems'].items() if v}
    all_ovl = copy.copy(overlays)
    all_ovl.update(special_overlays)
    default_fontsize = settings.get('default_fontsize', None)

    customization = {}
    for k, v in settings['co_efv'].items():
        if all_ovl.get(k, False):
            customization[k] = {kk: vv for kk, vv in v.items() if (vv is not None) or (kk == 't')}
            for kk in list(customization[k].keys()):  # List first because the dict could change during the loop
                if kk.startswith('pass_in') and len(customization[k][kk]) == 0:
                    # Remove empty pass_in_keywords / pass_in_args since they are nothing but clutter
                    customization[k].pop(kk, None)

    # Create a string that contains load instructions so it evaluates into a dict containing ODS instances
    load_instructions_dict = {index: settings['cases'][index].get('instructions_for_loading_ods', 'None') for index in settings['cases']}
    load_instructions_string = {index: 'replace_{}'.format(index) for index in settings['cases']}
    load_instructions_string = repr(load_instructions_string)
    for index in settings['cases']:
        load_instructions_string = load_instructions_string.replace("'replace_{}'".format(index), load_instructions_dict[index])

    _, default_profile_y_quantities = find_profile_y_options()

    contents = '''def plot_eq_cx():
    """
    Plots an equilibrium slice with a specific configuration of hardware overlay(s)

    Automatically generated function output by efitviewer. Please save this file somewhere permanent to avoid losing it.

    Generated {date:} by {user:} on {host:}
    OMFIT version: {omfit_version:}
    """

    from omfit_classes.omfit_efitviewer import plot_cx_ods, populate_efitviewer_figure
    device = {device:}
    shot = {shot:}
    cases = {cases:}
    odss = {load_instructions:}
    fig = pyplot.figure()
    gridspec_kw = {gridspec_kw:}
    cx_ax, profile_axs = populate_efitviewer_figure(
        fig,
        scratch,
        show_cx={show_cx:},
        num_profiles={num_profiles:},
        num_profile_cols={num_profile_cols:},
        profiles_sharex={profiles_sharex:},
        profiles_sharey={profiles_sharey:},
        **gridspec_kw
        )
    levels = {levels:}
    customization = {customization:}
    plot_cx_ods(
        cx_ax=cx_ax,
        profile_axs=profile_axs,
        odss=odss,
        cases=cases,
        contour_quantity={contour_quantity:},
        allow_fallback={allow_fallback:},
        levels=levels,
        plot_style_kw={plot_style_kw:},
        contour_resample_factor={contour_resample_factor:},
        xlim={xlim:},
        ylim={ylim:},
        overlays={overlays:},
        special_overlays={special_overlays:},
        customization=customization,
        default_fontsize={default_fontsize:},
        show_legend={show_legend:},
        profile_x_quantity={profile_x_quantity:},
        profile_y_quantities={profile_y_quantities:},
    )
    return

    '''.format(
        device=repr(device),
        shot=repr(shot),
        cases=repr(cases),
        load_instructions=load_instructions_string,
        contour_quantity=repr(settings['contour_quantity']),
        allow_fallback=repr(settings['allow_fallback']),
        levels=repr(settings['{}_levels'.format(settings['contour_quantity'])]),
        plot_style_kw=settings.setdefault('plot_style_kw', {}),
        contour_resample_factor=settings['contour_resample_factor'],
        xlim=repr(settings['xlim']),
        ylim=repr(settings['ylim']),
        overlays=repr(overlays),
        special_overlays=repr(special_overlays),
        customization=repr(customization),
        date=datetime.datetime.now(),
        user=getpass.getuser(),
        host=socket.gethostname(),
        omfit_version=repo.active_branch()[-1],
        default_fontsize=default_fontsize,
        show_legend=settings.setdefault('show_legend', 2),
        gridspec_kw=repr(settings['profiles'].get('gridspec_kw', {})),
        show_cx=settings.get('show_cx', True),
        num_profiles=settings['profiles'].get('num_profiles', 0),
        num_profile_cols=settings['profiles'].get('num_profile_cols', 0),
        profiles_sharex=repr(settings['profiles'].get('sharex', 'all')),
        profiles_sharey=repr(settings['profiles'].get('sharey', 'none')),
        profile_x_quantity=repr(settings['profiles'].get('xaxis_quantity', None)),
        profile_y_quantities=[
            settings['profiles'].get(f'yaxis_quantity_{i}', default_profile_y_quantities[i])
            for i in range(settings['profiles'].get('num_profiles', 0))
        ],
    )
    contents += '\nplot_eq_cx()'
    contents = omfit_formatter(contents)

    print('The following commands will generate the last saved equilibrium cross section plot:\n')
    printi(contents)
    print('')

    return contents


def dump_plot_command():
    """
    Writes a script for reproducing the equilibrium cross section plot based on current settings

    :return: (OMFITpythonTask, string)
        Reference to the script and its contents
    """
    from omfit_classes.omfit_python import OMFITpythonTask

    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    ods = out['efitviewer_ods']
    device = tokamak(ods['dataset_description.data_entry'].get('machine', settings['cases'][0]['device']))
    shot = ods['dataset_description.data_entry'].get('pulse', evalExpr(settings['cases'][0]['shot']))
    filename = settings.setdefault('export_script_filename', "saved_eq_cx_plot_{}_{}".format(device, shot))
    ext = os.extsep + 'py'
    if filename.endswith(ext):
        filename = filename[: -len(ext)]
    contents = dump_plot_command_content()
    script = out[filename] = OMFITpythonTask(filename + ext, fromString=contents)
    print("Script saved to out['{}']".format(filename))
    return script, contents


def box_plot_command(number=None, location=None):
    """
    Puts commands for reproducing the plot into the command box

    :param number: int
        Index (not visible number) of the command box to edit.
        Although normally an int, there are some special values:
            None: get number from location instead
            'new', 'New', or -1: create a new command box and use its number

    :param location: string
        Location in the tree where the command box number (not index) is stored

    :return: string
        String written to command box
    """
    if number is None:
        number_plus_1 = eval(location)
        number = number_plus_1 - 1 if is_numeric(number_plus_1) else number_plus_1
    if str(number).lower().startswith('new') or (number is None) or (is_numeric(number) and number < 0):
        number = add_command_box_tab()
    assert is_numeric(number)
    assert number >= 0
    contents = dump_plot_command_content()
    prior_cmd_box_contents = OMFITaux['GUI'].command[number].get()
    printw('Contents of command box index {}, #{} prior to overwriting with plot script:'.format(number, number + 1))
    printw('-' * 80)
    print(prior_cmd_box_contents)
    printw('-' * 80)
    printw('End of prior command box contents')
    OMFITaux['GUI'].command[number].set(contents)
    return contents


# GUI helpers -----------------------------------------------------------------------------------------------------
def add_case():
    """Extends the cases available for overlay by adding one case to the end"""
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    new_idx = np.max(list(settings['cases'].keys())) + 1
    settings['cases'][int(new_idx)] = SettingsName()  # new_idx must be int, not np.int64
    return


def delete_case(idx):
    """
    Removes a case from the list

    :param idx: int
        Index of case to delete

    :return: new_max: int
        New maximum case index, in case you wanted to know
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    assert idx > 0, "You're not allowed to delete the primary case. Naughty!"
    del settings['cases'][idx]
    new_max = np.max(list(settings['cases'].keys()))
    return new_max


def update_cx_time(location, index=None):
    """
    Updates list of times to use for overlays.
    In this way, the plot can be updated to add/remove diagnostics without forgetting time-slice overlay setup.

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update

    :param index: int
        Index of the case to update
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    printd(f'update_cx_time: {location}, index={index}', topic='efitviewer')
    new_time = eval(location)
    if index is None:
        try:
            index = int(location.split("['cases'][")[-1].split("]['time']")[0])
        except ValueError:
            try:
                index = int(location.split("scratch']['efitviewer_")[-1].split("_")[0])
            except ValueError:
                index = int(location.split("__scratch__']['efitviewer_")[-1].split("_")[0])
        printd(f'  update_cx_time: location = {location:}, index = {index:}', topic='efitviewer')
    if settings['overlay']:
        new_times = np.append(np.atleast_1d(settings['cases'].setdefault(index, SettingsName()).setdefault('time', None)), new_time)
    else:
        new_times = np.atleast_1d(new_time)
    settings['cases'].setdefault(index, SettingsName())['time'] = new_times

    plot_cx_ods(clear_first=True)
    return


def update_gui_figure(location=None, **kw):
    r"""
    Handle updates to the figure embedded in the GUI while setting defaults for appropriate keywords

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update

    :param \**kw: Additional keywords passed to plot_cx_ods
        You can override defaults
    """
    printd('updating figure after changing location: {}'.format(location))
    kw.setdefault('clear_first', True)
    kw.setdefault('gentle', True)
    plot_cx_ods(**kw)
    return


def update_overlay(location):
    """
    Updates times when overlay changes; used to clear old overlays when exiting overlay mode

    :param location: string
        Location in the OMFITtree of the setting that changed to trigger the overlay update
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    overlay = eval(location)
    if not overlay:
        for idx in settings['cases']:
            new_times = np.atleast_1d(settings['cases'][idx]['time'])[-1]
            settings['cases'][idx]['time'] = new_times
        update_gui_figure()
    return


def default_xylim(dev=None):
    """Updates current settings to match device defaults"""
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if dev is None:
        try:
            dev = out['efitviewer_ods']['dataset_description.data_entry.machine']
        except (KeyError, ValueError):
            dev = tokamak(settings['cases'][0]['device'])
    default_xlim = default_plot_limits.get(dev, {}).get('x', None)
    default_ylim = default_plot_limits.get(dev, {}).get('y', None)
    settings['xlim'] = default_xlim
    settings['ylim'] = default_ylim
    update_gui_figure()
    return


def grab_xylim(decimals=None):
    """
    Grabs current figure limits and updates settings so updated plots will preserve limits

    :param decimals: int
        How many decimal places to retain while rounding

    :return: xlim, ylim
        They are loaded into settings, so catching the return is not necessary
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    if decimals is None:
        decimals = settings.setdefault('xylim_grab_rounding_decimals', 3)

    def proccess_lim(a):
        if decimals is None or decimals < 0:
            return a
        return tuple([np.round(aa, decimals) if is_numeric(aa) else aa for aa in np.atleast_1d(a)])

    ax = scratch.get('efitviewer_cx_ax', None)
    if ax is not None:
        xlim = proccess_lim(ax.get_xlim())
        ylim = proccess_lim(ax.get_ylim())
        settings['xlim'] = xlim
        settings['ylim'] = ylim
    else:
        xlim = ylim = None
    return xlim, ylim


def load_contours():
    """
    Loads contours specified by custom_contour_spacing setup

    :return: float array of contour levels
        They are loaded into SETTINGS so you don't have to catch this, but you can, if you want to.
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    cq = settings['contour_quantity']
    cq_in = dict(psi='psin').get(cq, cq)
    spacing = settings['custom_contour_spacing']
    levels = setup_special_contours(contour_quantity=cq_in, spacing=spacing)
    settings['{}_levels'.format(cq)] = levels
    return levels


def get_default_snap_list(device):
    """
    Guess default snap list based on device
    :param device: str
    :return: dict
    """
    guesses = {'EAST': {'EFIT_EAST': 'EFIT_EAST'}, 'KSTAR': {'EFIT01': 'EFIT01', 'EFITRT1': 'EFITRT1'}}
    guesses['EAST_US'] = guesses['EAST']
    for gd in guesses.keys():
        if is_device(device, gd):
            return guesses[gd]
    return {}


def find_cq_options():
    """
    Determines what should be available as options for the contour quantity

    :return: tuple
        list: list of options (as strings)
        str: name of the recommended default contour quantity

    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    cq_opts = []
    if 'psi' in out['efitviewer_ods']['equilibrium.time_slice[0].profiles_2d[0]']:
        cq_opts += ['psi_norm', 'psi']
        if 'psi' in out['efitviewer_ods']['equilibrium.time_slice[0].profiles_1d']:
            # psi is used to interpolate, so 1d and 2d psi are both needed to support the 1d profiles.
            # Here are some popular ones:
            popular_from_1d = ['q', 'rho_tor', 'rho_tor_norm']
            for pf1 in popular_from_1d:
                if pf1 in out['efitviewer_ods']['equilibrium.time_slice[0].profiles_1d']:
                    cq_opts += [pf1]
    if 'phi' in out['efitviewer_ods']['equilibrium.time_slice[0].profiles_2d[0]']:
        cq_opts += ['phi']
    if len(cq_opts):
        default_contour_quantity = 'psi_norm' if 'psi_norm' in cq_opts else cq_opts[0]
    else:
        default_contour_quantity = None
    return cq_opts, default_contour_quantity


def find_profile_y_options(index=0, allow_2d=True, allow_constraints=True):
    """
    Finds a list of quantities that could go on the y axis of the profile plots

    :param index: int
        Index of time-slice to check in, in case different times have different availability (hopefully not)

    :param allow_2d: bool
        Allow 2D profiles to enter the list. These have to be sliced later to make 1D plots.

    :param allow_constraints: bool
        Allow constraint profiles to enter the list.
        These have to have associated functions for interpreting constraint data properly.

    :return: tuple
        list: all options for y axis quantities
        list: list of recommended defaults for each plot panel
    """
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
    yopts = [k for k, v in out['efitviewer_ods']['equilibrium']['time_slice'][index]['profiles_1d'].items() if isinstance(v, np.ndarray)]
    if 'j_tor' not in yopts:
        if index == 0:
            ods = out['efitviewer_ods']
        else:
            ods = out[f'efitviewer_ods_{index}']
        if calculate_j_toroidal(ods, 0, check_availability=True):
            yopts += ['j_tor']
    if allow_2d:
        yopts += [
            k for k, v in out['efitviewer_ods']['equilibrium']['time_slice'][index]['profiles_2d.0'].items() if isinstance(v, np.ndarray)
        ]
        if 'b_field_tor' not in yopts:
            yopts += ['b_field_tor']
    if allow_constraints:
        for k in out['efitviewer_ods']['equilibrium']['time_slice'][index]['constraints']:
            function_name = f'constraint_profile_{k}'
            try:
                eval(function_name)
            except NameError:
                pass
            else:
                yopts += [k]
    priorities = ['pressure', 'q', 'dpressure_dpsi', 'f_df_dpsi', 'phi']
    ydefault = [p for p in priorities if p in yopts]
    ydefault += [y for y in yopts if y not in ydefault]
    ydefault += yopts
    ydefault += [None] * 100
    return yopts, ydefault


def setup_default_profiles(index=0):
    """Loads a group of settings that will probably make for good-looking & interesting profiles"""
    out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()

    # Axis quantities
    desired_quantities = ['pressure', 'q', 'dpressure_dpsi', 'f_df_dpsi']
    quantities = [dq for dq in desired_quantities if dq in out['efitviewer_ods']['equilibrium']['time_slice'][index]['profiles_1d']]
    p = settings.setdefault('profiles', SettingsName())
    p['xaxis_quantity'] = 'rho_tor_norm'
    for i, q in enumerate(quantities):
        p[f'yaxis_quantity_{i}'] = q

    # Subplot counts
    settings['show_cx'] = True
    p['num_profiles'] = len(quantities)
    p['num_profile_cols'] = square_subplots(len(quantities), just_numbers=True)[1]

    # Figure arrangement: size, spacing, etc.
    settings['figsize'] = (10, 8)
    p['gridspec_kw'] = {'width_ratios': [1 + p['num_profile_cols']] + [1] * p['num_profile_cols']}
    layout_tag = f"cx-{p['num_profiles']}-{p['num_profile_cols']}"
    layout = (
        settings.setdefault('plot_style_kw', SettingsName())
        .setdefault('subplot_layout', SettingsName())
        .setdefault(layout_tag, SettingsName())
    )
    layout.update(dict(wspace=0.16, left=0.03, right=0.92))

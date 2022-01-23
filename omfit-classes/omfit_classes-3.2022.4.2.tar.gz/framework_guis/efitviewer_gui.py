# -*-Python-*-
# Created by eldond at 2019-12-23 08:43

"""
This script produces a GUI for managing EFIT-viewer style plots
"""

from omfit_classes.omfit_efitviewer import (
    omas_features,
    plot_cx_ods,
    load_cx_ods,
    update_cx_time,
    plot_grid,
    dump_plot_command,
    omas_features,
    grab_xylim,
    default_xylim,
    update_overlay,
    add_case,
    delete_case,
    setup_avail_systems,
    setup_special_contours,
    load_contours,
    pick_output_location,
    box_plot_command,
    get_default_snap_list,
    EfitviewerDataError,
    populate_efitviewer_figure,
    save_subplot_layout,
    find_cq_options,
    find_profile_y_options,
    setup_default_profiles,
    update_gui_figure,
)

from omfit_classes.omfit_efitviewer import update_gui_figure as update_figure
from omfit_classes.utils_fusion import available_EFITs

defaultVars(section='top_level', index=0, location=None, hw_sys=None)

# Link to related items
that = MainScratch['__efitviewer_support_gui__']
out_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
settings.setdefault('profiles', SettingsName())

if index == 0:
    ods_tag = 'efitviewer_ods'
else:
    ods_tag = 'efitviewer_ods_{}'.format(index)

if ods_tag in out:
    re_load = 'Reload (will overwrite current case) '
else:
    re_load = 'Load'


def top_level():
    """Top level of the efitviewer mk.2 GUI"""
    OMFITx.TitleGUI('efitviewer mk.2')

    with OMFITx.same_row():
        OMFITx.CompoundGUI(this, '', section='efitviewer_controls')
        OMFITx.CompoundGUI(this, '', section='efitviewer_figure')
    return


def efitviewer_figure(show_labels=True):
    """
    Provides the figure panel to the eftiviewer GUI

    :param show_labels: bool
        Enable an OMFITx.Label instance.

    :return: (Axes instance, OMFITx.Label() result)
    """
    label = None

    show_cx = settings.setdefault('show_cx', True)
    num_profiles = settings['profiles'].setdefault('num_profiles', 0)
    num_profile_cols = settings['profiles'].setdefault('num_profile_cols', 0)
    gridspec_kw = settings['profiles'].setdefault('gridspec_kw', {})

    if 'efitviewer_ods' in out:
        ods = out['efitviewer_ods']
        if 'dataset_description.data_entry.machine' in ods and 'dataset_description.data_entry.pulse' in ods:
            device = out['efitviewer_ods']['dataset_description.data_entry.machine']
            shot = out['efitviewer_ods']['dataset_description.data_entry.pulse']
            if show_labels:
                label = OMFITx.Label('{}#{}'.format(device, shot))
        elif show_labels:
            label = OMFITx.Label('Incomplete ODS. Please try reloading or loading a different case.')
    elif show_labels:
        label = OMFITx.Label('Waiting for ODS data to be loaded...')

    fig = scratch['efitviewer_fig'] = OMFITx.Figure(returnFigure=True, figsize=settings.setdefault('figsize', [5, 8]))
    cx_ax, profile_axs = populate_efitviewer_figure(
        fig,
        scratch,
        show_cx=show_cx,
        num_profiles=num_profiles,
        num_profile_cols=num_profile_cols,
        profiles_sharex=settings['profiles'].setdefault('sharex', 'all'),
        profiles_sharey=settings['profiles'].setdefault('sharey', 'none'),
        **gridspec_kw,
    )
    OMFITx.Entry(settings_loc + "['figsize']", 'Figure dimensions (cm)', default=[7, 8], updateGUI=True, width=5)
    with OMFITx.same_row():
        OMFITx.Button(
            'Save subplot layout',
            save_subplot_layout,
            width=5,
            help='Getting the right subplot spacing when the figure has a cross section and an arbitrary number '
            'of profile subplots is hard to do automatically. You can use the adjustment sliders to make '
            'the figure how you want it and then save your layout with this button. Each combination of cross '
            'section on/off, number of profiles, and number of columns for profiles will get a unique save, so '
            'you can switch back and forth between profile plot counts and your settings should be remembered.',
        )
        OMFITx.Button(
            'Forget saved layout',
            lambda: save_subplot_layout(reset=True),
            updateGUI=True,
            width=5,
            help='Delete a saved subplot layout so it will return to the global default settings. '
            'Layouts are saved for each combination of CX on/off, number of profile plots, and number of '
            'columns of profile plots, so you can save a different left margin for a figure with just a '
            'cross section from the left margin for a figure with 9 profiles in 3 columns in addition to '
            'the cross section..',
        )
    # OMFITx.CheckBox(settings_loc + "['auto_plot']", 'Automatic update', default=True, updateGUI=True)
    if 'efitviewer_ods' in out:
        if settings['auto_plot']:
            plot_cx_ods(clear_first=True, gentle=True)  # plot_cx_ods will get fig & ax from settings in scratch
        else:
            OMFITx.Button('Plot cross section', lambda: plot_cx_ods(clear_first=True, gentle=True))
    return cx_ax, label


def efitviewer_controls():
    """Provides the main control part of the efitviewer GUI"""

    # Choose G-file or device/shot/tree/time
    OMFITx.CompoundGUI(this, '', section='efitviewer_multi_case_selector')
    # The time overlay checkbox should be outside of the case-specific tabs
    OMFITx.CheckBox(settings_loc + "['overlay']", 'Overlay times', default=False, postcommand=update_overlay)

    if 'efitviewer_ods' in out:
        ods = out['efitviewer_ods']
        ods_valid = 'time' in ods['equilibrium'] and len(ods['equilibrium']['time_slice'][0]['profiles_2d'])
        if ods_valid:
            OMFITx.CompoundGUI(this, '', section='efitviewer_overlays')  # Choose hardware system overlays
            OMFITx.CompoundGUI(this, '', section='efitviewer_details')  # Stuff like figure setup, grid, etc.
        else:
            OMFITx.Label('ODS appears to be invalid. Try troubleshooting, then reloading.', fg='red')
            OMFITx.CompoundGUI(this, 'Troubleshooting tools', section='efitviewer_troubleshooting')
    else:
        OMFITx.Tab('Advanced')
        OMFITx.CompoundGUI(this, '', section='efitviewer_advanced')
    return


def efitviewer_advanced():
    """Advanced options"""
    OMFITx.CheckBox(
        settings_loc + "['no_empty']",
        'Remove empty time-slices from ODS',
        default=True,
        help='Inspect plasma current and number of boundary outline points at each time and '
        'remove time-slices where either of these is 0. Takes effect before MDSplus EFIT data are written to ODS.',
    )
    OMFITx.Entry(
        settings_loc + "['int_time_roundoff_threshold']",
        'Threshold for rounding times to integers (ms)',
        default=1e-2,
        help='Do you want to see 326 ms instead of 326.000000123 ms? Well, this is the setting for you!',
        updateGUI=True,
    )


def efitviewer_multi_case_selector():
    """Provides a sub-GUI for managing several case selectors for doing multi-shot overlays"""

    OMFITx.Tab('Primary case')
    OMFITx.CompoundGUI(this, '', section='efitviewer_case_selector', index=0)

    cases = settings['cases']

    for i in range(1, len(cases)):
        OMFITx.Tab('Case {}'.format(i))
        OMFITx.CompoundGUI(this, '', section='efitviewer_case_selector', index=i)
        OMFITx.Button('Delete this case', lambda idx=i: delete_case(idx), updateGUI=True)

    OMFITx.Tab('New case')
    OMFITx.Button('Add case', add_case, updateGUI=True)
    return


def time_selector(ods_tag):
    """
    Adds the time selector
    """
    try:
        efit_times = out[ods_tag]['equilibrium.time'] * 1000  # s to ms
    except (KeyError, ValueError):
        efit_times = None
    if efit_times is not None and len(tolist(efit_times)):
        rounded_times = np.around(efit_times).astype(int)
        integer_conversion_error = max(abs(efit_times - rounded_times))  # ms
        int_time_roundoff_threshold = settings.setdefault('int_time_roundoff_threshold', 1e-2)
        if integer_conversion_error < int_time_roundoff_threshold:  # ms
            efit_times = rounded_times
        if parent_settings['EXPERIMENT']['time'] is None:
            default_time = efit_times[0]
        else:
            default_time = efit_times[closestIndex(efit_times, parent_settings['EXPERIMENT']['time'])]
    else:
        default_time = None
    if index == 0:
        case_name = 'primary case'
    else:
        case_name = f'case {index}'
    OMFITx.ComboBox(
        "scratch['efitviewer_{}_time']".format(index),
        tolist(efit_times),
        f"Time for {case_name} ({settings['cases'][index]['device']}#{settings['cases'][index]['shot']}) (ms)",
        default=default_time,
        check=is_int,
        state='normal',
        postcommand=update_cx_time,
    )
    # t = settings['cases'][index].get('time', None)
    if settings['cases'][index].setdefault('time', None) is None:
        # noinspection PyBroadException
        try:
            settings['cases'][index]['time'] = scratch[f'efitviewer_{index}_time']
        except Exception:
            pass
    # OMFITx.CheckBox(settings_loc + "['overlay']", 'Overlay times', default=False, postcommand=update_overlay)


def add_status_label(index, data_source, show_status_label=True, color=None, text=None):
    """
    Adds a status label to the GUI

    :param index: int
        Index of this case, for differentiating between tabs for multi-shot display.

    :param data_source: str
        'MDS': data from MDSplus
        'tree': data from an object in the tree
        other: raises EfitviewerDataError

    :param show_status_label: bool
        Flag for enabling the label

    :param color: str
        Name of a color for the label foreground. If provided, it will be applied.

    :param text: str
        New text to use to update the label. If not provided, the label text will remain unchanged.
    """
    # In order to work properly, the content of 'select_text_var_#' in scratch has to be set by the client
    select_text_var = scratch.setdefault(f'select_text_var_{index}_{data_source}', tk.StringVar())

    if show_status_label:
        scratch[f'efitviewer_select_label_{index}_{data_source}'] = OMFITx.Label('', textvariable=select_text_var)
        update_status_label(index, data_source, color=color, text=text)
    else:
        scratch[f'efitviewer_select_label_{index}_{data_source}'] = None


def update_status_label(index, data_source, color=None, text=None):
    """
    Updates the status label

    :param index: int
        Index of this case, for differentiating between tabs for multi-shot display.

    :param data_source: str
        'MDS': data from MDSplus
        'tree': data from an object in the tree
        other: raises EfitviewerDataError

    :param color: str
        Name of a color for the label foreground. If provided, it will be applied.

    :param text: str [optional]
        New text to use to update the label. If not provided, the label text will remain unchanged.
    """
    label = scratch.setdefault(f'efitviewer_select_label_{index}_{data_source}', None)
    select_text_var = scratch.setdefault(f'select_text_var_{index}_{data_source}', tk.StringVar())
    if select_text_var is not None and text is not None:
        select_text_var.set(text)
    if label is not None:
        if color is not None:
            label.config(foreground=color)


def efitviewer_mds_selector(show_status_label=True):
    """
    Sets up the source of data from MDSplus

    :param show_status_label: bool
    """
    data_source = 'MDS'
    OMFITx.Entry(
        settings_loc + "['cases'][{}]['device']".format(index),
        'Device',
        check=is_string,
        default=tokamak(parent_settings['EXPERIMENT']['device']),
        updateGUI=True,
    )
    OMFITx.Entry(
        settings_loc + "['cases'][{}]['shot']".format(index),
        'Shot',
        check=is_int,
        default=evalExpr(parent_settings['EXPERIMENT']['shot']),
        updateGUI=True,
    )
    device = tokamak(settings['cases'][index]['device'])
    shot = settings['cases'][index]['shot']

    snap_list, efit_help = available_EFITs(scratch, device, shot, default_snap_list=get_default_snap_list(device), format='{tree}')

    e = OMFITx.ComboBox(
        settings_loc + "['cases'][{}]['efit_tree']".format(index),
        snap_list,
        'EFIT tree',
        state='normal',
        help=efit_help,
        updateGUI=True,
        default=list(snap_list.values())[0] if (len(snap_list) > 0) else None,
    )
    e.configure(width=40)
    efit_tree = settings['cases'][index]['efit_tree']

    OMFITx.CheckBox(
        f"{settings_loc}['minimal_eq_data']",
        "Load only minimal data",
        default=True,
        help='A minimal dataset should load faster, but will only support the cross section plot. '
        'Options for profile plots will be very limited.',
    )

    scratch[f'select_text_var_{index}_{data_source}'] = select_text_var = tk.StringVar()
    try:
        ods_device = out[ods_tag]['dataset_description.data_entry.machine']
        ods_shot = out[ods_tag]['dataset_description.data_entry.pulse']
        ods_comment = out[ods_tag]['dataset_description.ids_properties.comment']
    except (KeyError, ValueError):
        ods_device = None
        ods_shot = None
        ods_efit_tree = None
        ods_ready = False
    else:
        ods_efit_tree = ods_comment.split('EFIT tree = ')[-1]
        ods_ready = True
    if (efit_tree is None) or (shot is None) or (device is None):
        select_text_var.set('Select valid device, shot, and tree to proceed')
        select_text_color = 'black'
    elif not ods_ready:
        select_text_var.set('Ready to load')
        select_text_color = 'black'
    elif (shot != ods_shot) or (device != ods_device) or (efit_tree != ods_efit_tree):
        select_text_var.set('Press reload to update ODS to match new settings.')
        select_text_color = 'red'
    else:
        select_text_var.set('Current settings match ODS; ready to plot!')
        select_text_color = 'green'

    add_status_label(index, data_source, show_status_label, color=select_text_color)
    if efit_tree is not None and shot is not None and device is not None:
        OMFITx.Button(
            '{} {}#{} {}'.format(re_load, device, shot, efit_tree),
            lambda: load_cx_ods(gfile='unused', index=index),
            updateGUI=True,
        )
    return ods_tag


def compare_gfile_to_ods(gfile, ods, require_shot=True, require_efitid=False, require_device=False, require_times=True):
    """
    Compares as much information as possible in a gfile to that in an ods.

    Used for deciding how to update the status label when selecting a data source from the tree.

    :param gfile: dict-like, or OMFITgeqdsk
        A single OMFITgeqdsk can be used directly.
        A dict-like object, like an OMFITcollection or OMFITtree, must contain at least one OMFITgeqdsk instance.

    :param ods: ODS instance

    :param require_shot: bool
        Fail if shot can't be found for either source. Shot can usually be found in both.

    :param require_efitid: bool
        Fail if EFIT ID can't be found for either source. This isn't always easy to look up procedurally.

    :param require_device: bool
        Fail if device can't be found for either source. This isn't always easy to look up procedurally.

    :param require_times: bool
        Fail if times can't be found for either source. They are easy to find.

    :return: bool
        Flag indicating whether or not the gfile and ODS are consistent with each other.
    """

    ods_device = ods['dataset_description.data_entry.machine']
    ods_shot = ods['dataset_description.data_entry.pulse']
    ods_efitid = None
    ods_times = ods['equilibrium.time']

    # Get gfile times and a reference to a single OMFITgeqdsk instance
    if isinstance(gfile, OMFITgeqdsk):
        gfile0 = gfile
        gfile_times = np.array([int(gfile0.filename.split('.')[-1])]).astype(float)
    elif isinstance(gfile, dict):
        gfile_keys = [k for k, v in gfile.items() if isinstance(v, OMFITgeqdsk)]
        if not len(gfile_keys):
            raise EfitviewerDataError("This dictionary does not include any OMFITgeqdsk instances")
        gfile0 = gfile[gfile_keys[0]]
        gfile_times = np.array(gfile_keys).astype(float)
    else:
        raise EfitviewerDataError("gfile input to compare_gfile_to_ods() must be an OMFITgeqdsk or a dict-like")

    if (ods_times is not None) and (np.max(gfile_times) >= (900 * np.max(ods_times))):
        gfile_times *= 1e-3  # ms to s

    # Try to figure out geqdsk shot number
    if 'g' in gfile0.filename and '.' in gfile0.filename:
        try:
            gfile_shot_fn = int(gfile0.filename.split('g')[1].split('.')[0])
        except (ValueError, IndexError):
            gfile_shot_fn = None
    else:
        gfile_shot_fn = None
    try:
        gfile_shot_case = int(gfile0['CASE'][3].split('#')[1])
    except (IndexError, ValueError, KeyError):
        gfile_shot_case = None
    if gfile_shot_case is not None:
        gfile_shot = gfile_shot_case
    else:
        gfile_shot = gfile_shot_fn

    # Try to figure out geqdsk efitid
    try:
        gfile_efitid = gfile0['CASE'][5].strip()
    except (KeyError, IndexError, AttributeError):
        gfile_efitid = None

    # I don't know a standard for recording this
    gfile_device = None

    # Do the comparisons
    def do_comparison(gg, oo, rr, tag=''):
        if gg is not None and oo is not None:
            mm = not array_equal(gg, oo)
            printd(f'{ ["no mismatch", "mismatch"][int(mm)]} between {gg} and {oo}   {tag}', topic='efitviewer')
        elif rr:
            printd(f'mismatch between {gg} and {oo} because one is missing   {tag}', topic='efitviewer')
            mm = True
        else:
            printd(f'no mismatch between {gg} and {oo} because missing data are ignored   {tag}', topic='efitviewer')
            mm = False
        return mm

    device_mismatch = do_comparison(gfile_device, ods_device, require_device)
    shot_mismatch = do_comparison(gfile_shot, ods_shot, require_shot)
    efitid_mismatch = do_comparison(gfile_efitid, ods_efitid, require_efitid)
    times_mismatch = do_comparison(gfile_times, ods_times, require_times)
    return not (device_mismatch + shot_mismatch + efitid_mismatch + times_mismatch)


def efitviewer_tree_selector(show_status_label=True):
    """
    Setup for a data source in the OMFIT tree

    :param show_status_label: bool
    """
    data_source = 'tree'
    try:
        gtime0 = root['OUTPUTS']['gEQDSK'].keys()[0]
        default_g_file = "root['OUTPUTS']['gEQDSK']['{}']".format(gtime0)
    except (KeyError, IndexError):
        default_g_file = 'unused'
    OMFITx.TreeLocationPicker(
        settings_loc + "['cases'][{}]['gfile']".format(index), 'G-file(s) in tree', default=default_g_file, updateGUI=True
    )
    is_g = contains_g = None
    try:
        gfile_str = settings['cases'][index]['gfile']
        gfile = eval(settings['cases'][index]['gfile'])
        is_g = isinstance(gfile, OMFITgeqdsk)
        if isinstance(gfile, dict):
            gfiles = [k for k, v in gfile.items() if isinstance(v, OMFITgeqdsk)]
            contains_g = bool(len(gfiles))
        else:
            contains_g = False
            gfiles = None
        gfile_valid = is_g or contains_g
    except (KeyError, IndexError, TypeError, NameError):
        gfile_str = None
        gfile_valid = False
        case_info = ''
    else:
        if is_g:
            case_info = ' '.join(gfile['CASE'])
        elif contains_g:
            case_info = ' '.join(array(gfile[gfiles[0]]['CASE'])[array([0, 1, 2, 3, 5])])
        else:
            case_info = ''

    ods_loaded = ods_tag in out

    scratch[f'select_text_var_{index}_{data_source}'] = select_text_var = tk.StringVar()
    try:
        ods_source = out[ods_tag]['dataset_description.ids_properties.source']
    except (KeyError, ValueError):
        ods_source = None
    if (ods_source == gfile_str) and gfile_valid:
        if compare_gfile_to_ods(gfile, out[ods_tag]):
            select_text_var.set('Current settings match ODS; ready to plot!')
            select_text_color = 'green'
        else:
            select_text_var.set('Current GEQDSK location matches ODS, but a discrepancy was detected.')
            select_text_color = 'red'
    elif ods_loaded and gfile_valid:
        select_text_var.set('Press reload to update ODS to match new settings.')
        select_text_color = 'red'
    elif not ods_loaded and gfile_valid:
        select_text_var.set('Ready to load.')
        select_text_color = 'black'
    else:
        select_text_var.set('Select an OMFITgeqdsk or container of OMFITgeqdsk instances to continue.')
        select_text_color = 'black'

    add_status_label(index, data_source, show_status_label, color=select_text_color)
    if gfile_valid:
        OMFITx.Button('{} {}'.format(re_load, case_info), lambda: load_cx_ods(index=index), updateGUI=True)
    # else:
    # OMFITx.Label('Select an OMFITgeqdsk or container of OMFITgeqdsk instances to continue')
    return ods_tag


def efitviewer_case_selector(show_status_label=True):
    """
    Provides a sub-GUI with controls for choosing (device, shot, tree, time) or a g-file for efitviewer-style plots

    :param show_status_label: bool
        Add an OMFITx.Label() with the current status.
    """

    if index not in settings['cases']:
        OMFITx.Label(f"Index {index} is not ready. Possible corruption in settings['cases']", fg='red')
        OMFITx.End()

    OMFITx.ComboBox(
        f"{settings_loc}['cases'][{index}]['source']",
        {'Gather data from MDSplus': 'MDS', 'Gather a GEQDSK or collection of GEQDSKs from the tree': 'tree'},
        'Data source',
        default='MDS',
        updateGUI=True,
    )
    src = settings['cases'][index]['source']
    fn_name = f'efitviewer_{src.lower()}_selector'
    fn = eval(fn_name)
    fn(show_status_label=show_status_label)

    # Done with gEQDSK selection ----------------------------------------------------------------------------------
    OMFITx.Tab()

    if ods_tag in out:
        with OMFITx.same_row():
            OMFITx.CheckBox(
                settings_loc + "['cases'][{}]['active']".format(index),
                'Overlay equilibrium from this case',
                default=True,
                postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
            )
            OMFITx.Button(
                'Customize equilibrium...',
                lambda location=None, idx=index: that.run(section='efitviewer_equilibrium_customization', index=idx, out_loc=out_loc),
            )

    if ods_tag in out:
        time_selector(ods_tag)

    return


def efitviewer_overlays():
    """Provides a GUI panel for selecting hardware overlays for the efitviewer-style plot"""

    try:
        device = out['efitviewer_ods']['dataset_description.data_entry.machine']
    except (ValueError, KeyError):
        device = tokamak(parent_settings['EXPERIMENT']['device'])
    setup_avail_systems()
    for i, sys in enumerate(settings['systems'].keys()):
        if (i % 10) == 0:
            OMFITx.Tab('Overlays {}'.format(i))
        with OMFITx.same_row():
            OMFITx.CheckBox(
                settings_loc + "['systems']['{}']".format(sys),
                sys,
                default=False,
                postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
            )
            OMFITx.Button(
                'Customize...', lambda sys_=sys: that.run(hw_sys=sys_, section='co_efv_{}'.format(sys_), out_loc=out_loc), width=5
            )

    OMFITx.Tab('Overlays special')
    OMFITx.CompoundGUI(this, '', section='efv_so_general')

    dev_tag = 'efv_so_{}'.format(tokamak(device, output_style='GPEC'))
    OMFITx.Tab('Overlays {}'.format(device))
    try:
        OMFITx.CompoundGUI(this, '', section=dev_tag)
    except NameError:
        OMFITx.Label('No special instructions are defined for this device.')

    OMFITx.Tab('Profiles')  # -------------------------------------------------------------------------------------
    OMFITx.CompoundGUI(this, '', section='efitviewer_profile_setup')
    return


def efitviewer_details():
    """Provides a sub-GUI for changing details of the efitviewer tool"""

    # Setup  # ----------------------------------------------------------------------------------------------------
    try:
        device = out['efitviewer_ods']['dataset_description.data_entry.machine']
        shot = out['efitviewer_ods']['dataset_description.data_entry.pulse']
    except (KeyError, ValueError):
        device = tokamak(parent_settings['EXPERIMENT']['device'])
        shot = evalExpr(parent_settings['EXPERIMENT']['shot'])

    OMFITx.Tab('Axes')  # -----------------------------------------------------------------------------------------
    if True:  # For code folding, okay?
        with OMFITx.same_row():
            lim_help = 'Select axis limits for the plot in data units (probably m).'
            grab_help = 'Grab current axis limits from the figure as displayed and put them into the entry fields.'
            default_help = 'Set axis limits to reasonable defaults for the current device, if there are any on file.'
            # If using same_row: attach help to last item on the row. Otherwise, split it up.
            last_help = 'Control plot axis limits.\n\nEntry fields: {}\n\nGrab button: {}\n\nd button: {}'.format(
                lim_help, grab_help, default_help
            )
            OMFITx.Label('Limits (m):')
            OMFITx.Entry(settings_loc + "['xlim']", 'R', width=9, postcommand=update_figure)
            OMFITx.Entry(settings_loc + "['ylim']", 'Z', width=9, postcommand=update_figure)
            OMFITx.Button('Grab', grab_xylim, updateGUI=True, width=5)
            OMFITx.Button('d', default_xylim, updateGUI=True, width=1, help=last_help)

        with OMFITx.same_row():
            settings.setdefault('plot_style_kw', {}).setdefault('axes_aspect', 'equal_box')
            settings.setdefault('plot_style_kw', {}).setdefault('frame_on', True)

            OMFITx.ComboBox(
                settings_loc + "['plot_style_kw']['axes_aspect']",
                ['equal_box', 'equal_datalim', 'auto', 'None'],
                'Aspect',
                # default='equal_box',
                state='normal',
                postcommand=update_figure,
                width=6,
                help='"equal_box": forces even X/Y axis spacing by changing the axes dimensions. '
                '"equal_datalim": forces even X/Y axis spacing by changing data limits. '
                '"auto": allows uneven X/Y axis spacing. '
                'numeric: a circle will be stretched so its height is X times its width, where X is this setting. '
                'None: no action; aspect will be determined by some other script, such as a plot call in OMAS.',
            )
            OMFITx.CheckBox(settings_loc + "['plot_style_kw']['frame_on']", 'Frame')

        with OMFITx.same_row():
            settings.setdefault('plot_style_kw', {}).setdefault('tick_spacing', 0.25)
            settings.setdefault('plot_style_kw', {}).setdefault('xtick_loc', 'both')
            settings.setdefault('plot_style_kw', {}).setdefault('ytick_loc', 'both')
            OMFITx.Label('Ticks:')
            OMFITx.Entry(
                settings_loc + "['plot_style_kw']['tick_spacing']",
                'spacing (m)',
                # default=0.25,  # Default buttons make the GUI too wide
                postcommand=update_figure,
                width=5,
            )
            OMFITx.Label('Position:')
            OMFITx.ComboBox(
                settings_loc + "['plot_style_kw']['xtick_loc']",
                ['top', 'bottom', 'both'],
                'X',
                # default='both',
                postcommand=update_figure,
                width=6,
            )
            OMFITx.ComboBox(
                settings_loc + "['plot_style_kw']['ytick_loc']",
                ['left', 'right', 'both'],
                'Y',
                # default='both',
                postcommand=update_figure,
                width=6,
            )

        with OMFITx.same_row():
            OMFITx.CheckBox(
                settings_loc + "['plot_style_kw']['grid_enable']",
                'Show grid',
                default=False,
                postcommand=lambda location: plot_grid(enable=eval(location)),
            )
            OMFITx.Entry(
                settings_loc + "['plot_style_kw']['grid_kw']",
                'Grid keywords',
                default={},
                postcommand=lambda location: plot_grid(grid_kw=eval(location)),
                help='Dictionary of keywords to pass to grid(). '
                'Some options: color, linestyle, linewidth, alpha, ... . '
                'For more, see https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.grid.html',
            )

    OMFITx.Tab('Annotations')  # ----------------------------------------------------------------------------------
    if True:
        OMFITx.Entry(
            settings_loc + "['default_fontsize']",
            'OVERRIDE default annotation fontsize',
            default=None,
            help='12 is the default OMFIT size for the default OMFIT style. The current setting of '
            'rcParams["font.size"] is {}. Set this to None to leave rcParams alone. '
            'OMAS overlays specify relative font sizes by default, like xx-small or medium. '
            'These will scale with rcParams["font.size"].'.format(rcParams['font.size']),
            postcommand=update_figure,
        )
        OMFITx.ComboBox(
            settings_loc + "['show_legend']", {'always': 1, 'automatic': 2, 'never': 0}, 'Show legend', default=2, postcommand=update_figure
        )
        OMFITx.ComboBox(
            settings_loc + "['show_cornernote']",
            {'always': 1, 'automatic': 2, 'never': 0},
            'Show cornernote',
            default=2,
            postcommand=update_figure,
        )
        with OMFITx.same_row():
            settings.setdefault('plot_style_kw', {}).setdefault('subplot_label', None)
            settings.setdefault('plot_style_kw', {}).setdefault('subplot_label_corner', [1, 1])

            OMFITx.ComboBox(
                settings_loc + "['plot_style_kw']['subplot_label']",
                {'': None, '(a)': 0, '(b)': 1, '(c)': 2, '(d)': 3, '(e)': 4, '(f)': 5, '(g)': 6, '(h)': 7},
                'Add subplot label',
                width=5,
                postcommand=update_figure,
            )
            OMFITx.ComboBox(
                settings_loc + "['plot_style_kw']['subplot_label_corner']",
                {'top right': [1, 1], 'top left': [0, 1], 'bottom right': [1, 0], 'bottom left': [0, 0]},
                '',
                postcommand=update_figure,
                width=5,
            )

    OMFITx.Tab('Contours')  # -------------------------------------------------------------------------------------
    if True:
        if compare_version(omas.__version__, omas_features['contour_quantity']) >= 0:
            cq_opts, default_contour_quantity = find_cq_options()
            if len(cq_opts):
                OMFITx.ComboBox(
                    settings_loc + "['contour_quantity']",
                    cq_opts,
                    'Contour quantity',
                    default=default_contour_quantity,
                    updateGUI=True,
                    state='normal',
                )
            else:
                OMFITx.Label('No phi or psi data found in equilibrium 2d profiles! Contours unavailable!', fg='red')
                settings.setdefault('contour_quantity', 'rho')  # Make sure it's defined
        else:
            # Wasn't controlled well in OMAS 0.49.1 and earlier, but the default if all data are available was rho
            settings['contour_quantity'] = 'rho'

        bcl = np.r_[0.1:10:0.1]
        default_contour_levels = {'q': [1, 2, 2.5, 3, 4, 5, 6]}.get(settings['contour_quantity'], bcl)

        OMFITx.Entry(
            settings_loc + "['{}_levels']".format(settings['contour_quantity']),
            'Contour levels',
            default=default_contour_levels,
            postcommand=update_figure,
        )

        OMFITx.Button('Set up contours relative to reference...', lambda: that.run(section='efitviewer_contour_picker', out_loc=out_loc))

        if compare_version(omas.__version__, omas_features['sf']) >= 0:
            OMFITx.Entry(
                settings_loc + "['contour_resample_factor']",
                'Resample factor',
                default=3,
                help='Resampling 2d data to higher resolution makes smoother contours.',
                postcommand=update_figure,
            )

    OMFITx.Tab('Export')  # ---------------------------------------------------------------------------------------
    if True:
        OMFITx.Entry(
            settings_loc + "['export_script_filename']",
            'Filename for plot script',
            default="saved_eq_cx_plot_{}_{}".format(device, shot),
            help='The extension will be added.',
        )
        OMFITx.Button('Save plot commands to script', dump_plot_command)

        settings.setdefault('command_box_number', 'new tab')
        OMFITx.ComboBox(
            settings_loc + "['command_box_number']",
            ['new tab'] + list(range(1, 1 + len(OMFITaux['GUI'].command))),
            'Save plot commands to command box #',
            postcommand=box_plot_command,
        )

    OMFITx.Tab('Troubleshoot')  # ---------------------------------------------------------------------------------
    if True:
        OMFITx.CompoundGUI(this, '', section='efitviewer_troubleshooting')

    OMFITx.Tab('Advanced')  # -------------------------------------------------------------------------------------
    if True:
        OMFITx.CompoundGUI(this, '', section='efitviewer_advanced')

    return


def efitviewer_troubleshooting():
    """Provides a GUI for managing troubleshooting options"""
    OMFITx.Button(
        'Reset SSH tunnels, database connections',
        OMFIT.reset_connections,
        help='If the ODS is missing data, try resetting connections and then reloading it.',
    )
    return


def efv_so_general():
    """
    Provides a sub-GUI for handling EFitViewer Special Overlays (efv-so) that are general to all/most devices
    """
    # Custom script
    with OMFITx.same_row():
        OMFITx.CheckBox(
            settings_loc + "['special_systems']['custom_script']",
            'custom_script',
            default=False,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )

        OMFITx.Button('Configure custom script overlay...', lambda: that.run(section='co_efv_custom_script', out_loc=out_loc))

    # Scaled boundary
    with OMFITx.same_row():
        OMFITx.CheckBox(
            settings_loc + "['special_systems']['scaled_boundary']",
            'scaled_boundary',
            default=False,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )

        OMFITx.Button('Configure scaled boundary overlay...', lambda: that.run(section='co_efv_scaled_boundary', out_loc=out_loc))

    # Alternative limiter
    with OMFITx.same_row():
        OMFITx.CheckBox(
            settings_loc + "['special_systems']['alt_limiter']",
            'alt_limiter',
            default=False,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )

        OMFITx.Button('Configure alternative limiter overlay...', lambda: that.run(section='co_efv_alt_limiter', out_loc=out_loc))
    return


def efv_so_d3d():
    """
    Provides a sub-GUI for controlling EFitViewer Special Overlays (EFV-SO) that are specific to the DIII-D device
    """

    # BES is not in the IMAS schema yet as far as I can tell, so it goes under special
    with OMFITx.same_row():
        OMFITx.CheckBox(
            settings_loc + "['special_systems']['beam_emission_spectroscopy']",
            'beam_emission_spectroscopy',
            default=False,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )

        OMFITx.Button(
            'Customize...', lambda: that.run(hw_sys='beam_emission_spectroscopy', section='co_efv_generic', out_loc=out_loc), width=5
        )
    return


def efitviewer_profile_setup():
    """Adds controls for setting up profile displays"""
    OMFITx.Button("Load default profiles setup", setup_default_profiles, updateGUI=True)
    with OMFITx.same_row():
        OMFITx.CheckBox(
            f"{settings_loc}['show_cx']",
            'Show cross-section',
            default=True,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )
        OMFITx.Entry(
            f"{settings_loc}['profiles']['num_profiles']",
            'Number of profiles',
            default=0,
            check=is_int,
            updateGUI=True,
            width=2,
        )
        OMFITx.Entry(
            f"{settings_loc}['profiles']['num_profile_cols']",
            'Number of profile columns',
            default=0,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
            width=2,
        )
    OMFITx.Entry(
        f"{settings_loc}['profiles']['gridspec_kw']",
        'Keywords to pass to gridspec',
        default={},
        help="See gridspec documentation for details. width_ratios is especially useful here, as in {'width_ratios': [2, 1, 1]}",
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    nprof = settings['profiles']['num_profiles']
    if nprof > 0:
        cq_opts, dcq = find_cq_options()
        yopts, ydefault = find_profile_y_options(index)
        with OMFITx.same_row():
            OMFITx.ComboBox(
                f"{settings_loc}['profiles']['sharex']",
                ['none', 'col', 'row', 'all'],
                "Share X axes",
                default='all',
                postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
            )
            OMFITx.ComboBox(
                f"{settings_loc}['profiles']['sharey']",
                ['none', 'col', 'row', 'all'],
                "Share Y axes",
                default='none',
                postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
            )
        OMFITx.CheckBox(
            f"{settings_loc}['profiles']['last_col_right_label']",
            'Put Y-axis labels on the right for the last column',
            default=True,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )
        OMFITx.ComboBox(
            f"{settings_loc}['profiles']['xaxis_quantity']",
            cq_opts + ['r_outboard'],
            "X axis quantity",
            default=dcq,
            state='normal',
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )
        # Plan out arrangement of y axis selectors
        ncol = settings['profiles']['num_profile_cols']
        if ncol == 0:
            ncol = 1
        num_rows = int(np.max([np.ceil(nprof / float(ncol)), 1]))
        profiles_scratch = np.empty([num_rows, ncol], bool)
        profiles_scratch[:] = False
        for i in range(nprof):
            row = i % num_rows
            col = i // num_rows
            profiles_scratch[row, col] = True
        # Make Y axis quantity selectors
        for j in range(ncol):
            OMFITx.Tab(f'Prof col {j}')
            for i in range(num_rows):
                number = i * ncol + j
                if profiles_scratch[i, j]:
                    OMFITx.ComboBox(
                        f"{settings_loc}['profiles']['yaxis_quantity_{number}']",
                        yopts,
                        f'Y-axis quantity for plot {number}, row {i}, col {j}',
                        default=ydefault[number],
                        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                    )


# Call the specified section
printd('Launch efitviewer_gui for section = {}'.format(section), topic='efitviewer')
eval(section)()

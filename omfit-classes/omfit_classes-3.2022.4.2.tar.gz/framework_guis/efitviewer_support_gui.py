# -*-Python-*-
# Created by eldond 2020-04-07 20:34

"""
This script contains supporting GUIs for efitviewer
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
)

from omfit_classes.omfit_efitviewer import update_gui_figure as update_figure

defaultVars(section='co_efv_generic', index=0, location=None, hw_sys=None, out_loc=None)
if out_loc is None:
    output_loc, settings_loc, out, settings, parent_settings, scratch = pick_output_location()
else:
    output_loc = out_loc
    out = eval(out_loc)
    settings_loc = out_loc + "['SETTINGS']"
    settings = eval(settings_loc)


def co_efv_generic():
    """
    Provides an interface to support Customization of Overlays for EFitViewer for generic hardware
    """

    OMFITx.TitleGUI('efitviewer overlay customization ({})'.format(hw_sys))

    # Complain about problems and exit early if there are any
    if hw_sys is None:
        OMFITx.Label('You must specify a hardware system to customize when launching.')
        OMFITx.End()

    special = False
    if hw_sys not in settings['systems'] and hw_sys not in settings['special_systems']:
        OMFITx.Label("{} isn't a recognized hardware system. Perhaps this will work after you load the main efitviewer GUI.".format(hw_sys))
        OMFITx.Label('Valid main options:\n{}'.format('\n'.join(settings['systems'])))
        OMFITx.Label('Valid special options:\n{}'.format('\n'.join(settings['special_systems'])))
        OMFITx.End()
    elif hw_sys not in settings['systems']:
        special = True

    # settings = settings['co_efv'].setdefault(hw_sys, SettingsName())
    ods = out.get('efitviewer_ods', ODS())

    # Try to find the plot method and get its docstring
    po_method_name = 'plot_{}_overlay'.format(hw_sys)
    po_method = getattr(ods, po_method_name, None)
    if po_method is None:
        po_method = getattr(omfit_classes.omfit_efitviewer, po_method_name, None)
    if po_method is None:
        OMFITx.Label('Could not find plot method for {}; unable to display help')
    else:
        settings['co_efv'].setdefault(hw_sys, SettingsName())
        pom_doc_0 = po_method.__doc__
        pom_doc = copy.copy(pom_doc_0)
        p = ':param '
        while p in pom_doc:
            sp = pom_doc.split(p)
            this_par = sp[1]
            if len(sp) > 2:
                pom_doc = p.join([''] + sp[2:])
            else:
                pom_doc = ''
            par_name = this_par.split(':')[0]
            par_description = ':'.join(this_par.split(':')[1:])
            par_description = par_description.split(':return:')[0]
            if par_name in ['ods', 'ax']:
                pass
            elif par_name.startswith('**') or par_name.startswith(r'\**'):
                par_name = par_name.split('**')[1]
                OMFITx.Entry(
                    settings_loc + r"['co_efv']['{}']['pass_in_keywords_{}']".format(hw_sys, par_name),
                    'Additional keywords ({})'.format(par_name),
                    help=par_description,
                    default={},
                    postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                )
                generic_note = (
                    '\n\nThis is a generic setting that is respected by most OMAS plot overlays. It would '
                    'normally be caught in **kw, but its control has been separated out for convenience. '
                    'A redundant specification for this setting in kw will override this one.'
                )
                if not special:
                    OMFITx.Entry(
                        settings_loc + r"['co_efv']['{}']['labelevery']".format(hw_sys),
                        '    labelevery',
                        help=r'Controls which points are labeled. Typically, 0 turns labels off, '
                        r'1 labels every item, 2 labels every item, and so on. ' + generic_note,
                        default=None,
                        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                    )
                    OMFITx.Entry(
                        settings_loc + r"['co_efv']['{}']['notesize']".format(hw_sys),
                        '    notesize',
                        help='Controls size of annotations like point labels' + generic_note,
                        default=None,
                        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                    )
                    OMFITx.Entry(
                        settings_loc + r"['co_efv']['{}']['mask']".format(hw_sys),
                        '    mask',
                        help='Controls which items are displayed. Specify a list of bools that matches the '
                        'number of items that will be plotted.' + generic_note,
                        default=None,
                        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                    )
                    if compare_version(omas.__version__, '0.50.0') >= 0:
                        # These will crash omas plot methods if passed to incompatible versions
                        OMFITx.Entry(
                            settings_loc + r"['co_efv']['{}']['label_ha']".format(hw_sys),
                            '    label_ha',
                            help='Controls horizontal alignment of labels. Should be a string or list of strings. '
                            'Replacing one element with None triggers automatic alignment for that element. '
                            'If the list is too short, newer OMAS versions will be pad it with None (auto). '
                            'The required length is the number of items to label after selection and masking. '
                            'Options: "left", "right", "center".' + generic_note,
                            default=None,
                            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                        )
                        OMFITx.Entry(
                            settings_loc + r"['co_efv']['{}']['label_va']".format(hw_sys),
                            '    label_va',
                            help='Controls vertical alignment of labels. Should be a string or list of strings. '
                            'Replacing one element with None triggers automatic alignment for that element. '
                            'If the list is too short, newer OMAS versions will be pad it with None (auto). '
                            'The required length is the number of items to label after selection and masking. '
                            'Options: "top", "bottom", "center", "baseline", "center_baseline".' + generic_note,
                            default=None,
                            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                        )

                        OMFITx.Entry(
                            settings_loc + r"['co_efv']['{}']['label_r_shift']".format(hw_sys),
                            '    label_r_shift',
                            help='Add offsets to the R coordinates (data units, probably m) of all labels.\n'
                            'Scalar: add the same offset to every label.\n'
                            'Array-like: Allows different offsets for different labels. '
                            'Input will be padded with 0s to meet required length, which is the number of items '
                            'shown (the required length changes if items are removed using selection and masking '
                            'keywords). Older versions of OMAS only support scalars.' + generic_note,
                            default=0.0,
                            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                        )
                        OMFITx.Entry(
                            settings_loc + r"['co_efv']['{}']['label_z_shift']".format(hw_sys),
                            '    label_z_shift',
                            help='Add offsets to the Z coordinates (data units, probably m) of all labels.\n'
                            'Scalar: add the same offset to every label.\n'
                            'Array-like: Allows different offsets for different labels. '
                            'Input will be padded with 0s to meet required length, which is the number of items '
                            'shown (the required length changes if items are removed using selection and masking '
                            'keywords). Older versions of OMAS only support scalars.' + generic_note,
                            default=0.0,
                            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                        )
            elif par_name.startswith('*') or par_name.startswith(r'\*'):
                par_name = par_name.split('*')[1]
                OMFITx.Entry(
                    settings_loc + r"['co_efv']['{}']['pass_in_args_{}']".format(hw_sys, par_name),
                    'Additional args ({})'.format(par_name),
                    help='WARNING: Not ready to support positional arguments. This will not work.\n' + par_description,
                    default=(),
                    postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                    fg='red',
                )
            else:
                OMFITx.Entry(
                    settings_loc + r"['co_efv']['{}']['{}']".format(hw_sys, par_name),
                    par_name,
                    help=par_description,
                    default=None,
                    postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
                )
    return


def co_efv_scaled_boundary():
    """Provides a small GUI for configuring the scaled boundary overlay in EFITviewer"""

    OMFITx.TitleGUI('efitviewer overlay customization (scaled boundary)')

    default_mds_trees = {'DIII-D': 'EFIT01', 'EAST': 'EFIT_EAST'}

    sloc = settings_loc + "['co_efv']['scaled_boundary']"
    sets = settings['co_efv'].setdefault('scaled_boundary', SettingsName())

    OMFITx.Entry(sloc + "['device']", 'Device', default='ITER', postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True))
    sbd = sets['device']
    OMFITx.Entry(
        sloc + "['mds_tree']",
        'MDSplus tree',
        default=default_mds_trees.get(sbd, ''),
        help='may be ignored for future devices',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['shot']",
        'Shot',
        help='may be ignored for future devices',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['time']",
        'Time (ms)',
        help='may be ignored for future devices',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['scale']",
        'Scale factor (pre-offset)',
        default=1 / 3.68 if is_device(sbd, 'ITER') else 1,
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(sloc + "['x_offset']", 'R offset (m)', default=0, postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True))
    OMFITx.Entry(
        sloc + "['y_offset']",
        'Z offset (m)',
        default=-0.88 / 3.68 if is_device(sbd, 'ITER') else 0,
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['pass_in_keywords_kw']",
        'Plot keywords',
        default={},
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )

    OMFITx.Button('Update', OMFITx.Refresh, updateGUI=True)
    return


def co_efv_custom_script():
    """
    This script creates a GUI for managing options input to a custom overlay script
    """

    OMFITx.TitleGUI('efitviewer overlay customization (custom script)')

    OMFITx.Label('The overlay manager can call the .runNoGUI() method of an OMFITpythonTask instance.')
    OMFITx.Label(
        '''
    The keywords ax and ods will be provided to the .runNoGUI() call
    to pass an Axes instance and an ODS instance. Your script should
    include a defaultVars() call at the top that at minimum accepts
    these keywords. For example: defaultVars(ax=None, ods=None).

    To pass other keywords, enter a dictionary under the
    defaultvars_keywords setting. The complete call is:
    SCRIPT.runNoGUI(ax=ax, ods=ods, **defaultvars_keywords)

    For an example, see the script indicated by the default
    value of "script_loc".'''
    )

    OMFITx.TreeLocationPicker(
        settings_loc + "['co_efv']['custom_script']['script_loc']",
        'script_loc',
        default="OMFIT['EFITtime']['PLOTS']['efitviewer']['example_custom_overlay']",
        help='Location in the OMFIT tree of an OMFITpythonTask instance. Its .runNoGUI() method will be called in '
        'order to generate the overlay. It should have a defaultVars() entry that accepts keywords ax and ods. '
        'It can also accept others that you want to pass using the defaultVars_keywords option..',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )

    OMFITx.Entry(
        settings_loc + "['co_efv']['custom_script']['defaultvars_keywords']",
        'defaultvars_keywords',
        default={},
        help="Dictionary of keywords and values to pass to the script's defaultVars(), in addition to ods and ax.",
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    return


def co_efv_alt_limiter():
    """
    This script provides a GUI for customizing an alternative limiter overlay
    """

    OMFITx.TitleGUI('efitviewer overlay customization (alternative limiter)')

    sloc = settings_loc + "['co_efv']['alt_limiter']"

    if compare_version(omas.__version__, omas_features['show_wall']) >= 0:
        OMFITx.CheckBox(
            sloc + "['retain_wall']",
            'Also show limiter from ODS',
            default=True,
            postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
        )
    OMFITx.TreeLocationPicker(
        sloc + "['alt_limiter_data_loc']",
        'Alternative limiter data location',
        default="OMFIT['EFITtime']['TEMPLATES']['limiters']['2020-03-23_limiter']['data']",
        help='Limiter data should be an N*2 float array, ' 'where lim[:, 0] gives the R coordinates, and lim[:, 0] gives Z.',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['alt_limiter_data_array']",
        'Alt limiter data, manual entry',
        default=None,
        help='Limiter data should be a N*2 float array, where lim[:, 0] gives the R coordinates, and lim[:, 1] '
        'gives Z. If data are manually entered here, they will override data from a tree location (above).',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    OMFITx.Entry(
        sloc + "['scale']",
        'Scale limiter by factor',
        default=1.0,
        help='Use this to convert units to m.',
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )

    OMFITx.Entry(
        sloc + "['pass_in_keywords_kw']",
        'Additional keywords (kw)',
        default={},
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )
    return


def efitviewer_equilibrium_customization():
    """
    Provides a GUI for customizing individual equilibrium cross section plots
    """

    OMFITx.TitleGUI('Equilibrium customization for case {}'.format(index))

    OMFITx.CheckBox(
        settings_loc + "['cases'][{}]['wall']".format(index),
        'Include wall with equilibrium',
        default=True,
        postcommand=lambda location: plot_cx_ods(clear_first=True, gentle=True),
    )

    OMFITx.Entry(
        settings_loc + "['cases'][{}]['eqkw']".format(index),
        'Keywords to pass to plot() & contour(): drawing equilibrium'.format(index),
        default={},
        help="Specify a dictionary like `dict(color='r')`",
        postcommand=update_figure,
    )

    if compare_version(omas.__version__, omas_features['xkw']) >= 0:
        OMFITx.Entry(
            settings_loc + "['cases'][{}]['xkw']".format(index),
            'Keywords to pass to plot(): drawing X-points'.format(index),
            default={'marker': 'x'},
            help='Set marker to "" to disable X-point display',
            postcommand=update_figure,
        )


def efitviewer_contour_picker():
    """GUI for picking contour levels relative to some reference point"""

    OMFITx.TitleGUI('efitviewer: special contour level selection')

    settings.setdefault('custom_contour_spacing', SettingsName())
    cq = settings['contour_quantity']

    OMFITx.Label(
        "Use this feature to support tasks like finding the flux surface that's 1 cm\n"
        "outboard of the midplane, or 3 cm away from the outer strike point."
    )

    OMFITx.ComboBox(
        settings_loc + "['custom_contour_spacing']['quantity']",
        ['R', 'S', 'psi_n', 'psi'],
        'Custom contour spacing in terms of quantity',
        default='R',
        help='R is major radius in m.\n'
        'S is distance along the wall in m.\n'
        'psi_n is normalized poloidal flux.\n'
        'psi is poloidal flux prior to normalization.',
    )

    OMFITx.ComboBox(
        settings_loc + "['custom_contour_spacing']['reference']",
        ['outer_midplane', 'outer_lower_strike', 'outer_upper_strike'],
        'Reference point (ignored for flux quantities like psi)',
        default='outer_midplane',
    )

    OMFITx.Entry(
        settings_loc + "['custom_contour_spacing']['amount']",
        'Contour spacing amount (data units relative to reference)',
        default=[0, 0.1],
        help='The reference point is the LCFS for flux quantities. Otherwise, select the reference above.',
    )

    OMFITx.Button('Load custom {} contours'.format(cq), load_contours, updateGUI=True)
    return


# Call the specified section
try:
    eval(section)()
except NameError:
    if section.startswith('co_efv_'):
        # If a specific customization menu isn't found, fall back to the generic one
        co_efv_generic()
    else:
        raise

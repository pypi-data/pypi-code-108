print('Loading OMFIT APIs...')

try:
    # framework is running
    from .startup_choice import *

    # Don't do this if building the documentation
    if not any(('sphinx' in k and not 'sphinxcontrib' in k) for k in sys.modules):
        # here we do a `from pylab import *` to allow GUIs to evaluate user input
        from pylab import *
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

from omfit_classes import utils_base
from omfit_classes.utils_base import _streams
from omfit_classes.omfit_base import *
from omfit_classes.omfit_data import *
from omfit_classes import omfit_mds
from omfit_classes.omfit_mds import *
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_python import _OMFITpython
from omfit_classes.omfit_environment import OMFITenv
from omfit_classes.omfit_weblink import openInBrowser

import tkinter as tk
from tkinter import ttk
from glob import glob as _glob
import numpy as np
import re
import copy
import subprocess
from collections.abc import Callable as CollectionsCallable

# Decorator @_available_to_user is used to define which functions should appear in the OMFIT documentation
def _available_to_userTASK(f):
    OMFITaux.setdefault('OMFITxTASK_functions', [])
    OMFITaux['OMFITxTASK_functions'].append(f)
    OMFITaux['OMFITxTASK_functions'].sort(key=lambda x: str(x).lower())
    return f


def _available_to_userGUI(f):
    OMFITaux.setdefault('OMFITxGUI_functions', [])
    OMFITaux['OMFITxGUI_functions'].append(f)
    OMFITaux['OMFITxGUI_functions'].sort(key=lambda x: str(x).lower())
    return f


# This dictionary is used to keep track of the open GUIs
_GUIs = {}

# This dictionary is used to keep track of the inner workings of the active GUI
_aux = {}
_aux['topGUI'] = None
_aux['open_tabs'] = {}
_aux['parentGUI'] = None
_aux['is_compoundGUI'] = False
_aux['notebook'] = None
_aux['compoundGUIid'] = None
_aux['compoundGUIcounter'] = None
_aux['tab_list'] = {}
_aux['tab_name'] = ''
_aux['configure_size'] = []
_aux['harvest'] = {}
_aux['same_row'] = None
_aux['packing'] = 'top'  # tk.TOP # we use 'top' instead of 'tk.top' to avoid importing tk environment when only OMFIT classes are loaded

# ------------------------------------
# Nice representation of floats
# ------------------------------------
_originalPrintOptions = np.get_printoptions()


def repr(value):
    '''
    repr modified to work for GUI functions
    '''

    if xarray is not None and isinstance(evalExpr(value), DataArray):
        value = value.values
    if isinstance(value, np.ndarray) and len(value.shape) == 0:
        value = np.atleast_1d(value)[0]

    np.set_printoptions(formatter={'float': repr})
    try:
        if isinstance(evalExpr(value), float):
            if np.isnan(evalExpr(value)):
                value = 'nan'
            elif np.isinf(evalExpr(value)):
                if np.sign(evalExpr(value)) > 0:
                    value = 'inf'
                else:
                    value = '-inf'
            else:
                value = '{:.15g}'.format(value)
                if '.' not in value and 'e' not in value:
                    tmp = re.sub('[1-9]', 'x', value[::-1])
                    if 'x' in tmp:
                        index = int((tmp.index('x')) // 3 * 3)
                        if index != 0:
                            value = value[:-index] + 'e{:d}'.format(index)
                        else:
                            value = value + '.0'
                    else:
                        value = value + '.0'
        elif isinstance(value, np.ndarray) and len(value.shape) == 1:
            value = '[' + ', '.join(map(repr, np.atleast_1d(value))) + ']'
        elif isinstance(value, uncertainties.UFloat):
            value = f'ufloat({value.n},{value.s})'
        else:
            value = builtins.repr(value)
    finally:
        np.set_printoptions(**_originalPrintOptions)

    return value


def repr_eval(location, preentry=None, collect=False):
    '''
    evaluate location and provide representation
    '''
    value = _eval(location)

    if preentry is None:

        def preentry(val):
            return val

    if not isinstance(location, str) and collect:
        if np.all(np.atleast_1d(value) == value[0]):
            value = value[0]

    return repr(preentry(value))


# ------------------------------------
# GUI management
# ------------------------------------
class GUI(object):
    """
    This class creates a new GUI. It is used internally by OMFIT when a OMFITpythonGUI object is executed

    :param pythonFile: OMFITpythonGUI object to be executed

    :return: None
    """

    def __init__(self, pythonFile, relativeLocations, **kw):

        if OMFITaux['rootGUI'] is None:
            raise Exception('OMFIT GUI elements can only run within full OMFIT graphical framework')

        top = tk.Toplevel(OMFITaux['rootGUI'])
        top.withdraw()
        top.transient(OMFITaux['rootGUI'])

        top.protocol("WM_DELETE_WINDOW", lambda top=top: _clearClosedGUI(top))

        top.wm_title(treeLocation(pythonFile)[-1])

        # register GUI
        _GUIs[str(top)] = self

        self.top = top
        self.pythonFile = pythonFile
        self.notebooks = {}
        self.kw = kw
        self.locked = []
        self.relativeLocations = relativeLocations

        try:
            thereWasError = True
            self.update()
            top.update_idletasks()
            tk_center(top, parent=OMFITaux['rootGUI'])
            if len(self.parentGUI.winfo_children()):
                top.deiconify()
                top.lift()
                thereWasError = False
        except Exception:
            raise
        finally:
            if thereWasError:
                _clearClosedGUI(top)

    def update(self):
        try:
            _aux['topGUI'] = top = self.top
            _aux['compoundGUIid'] = str(id(self.pythonFile))
            _aux['compoundGUIcounter'] = 0

            # if there was a notebook, store the info about what tabs were selected
            _aux['open_tabs'] = {}
            for cg, nb in self.notebooks.items():
                index = nb.tabs().index(nb.select())
                _aux['open_tabs'][cg] = index

            if hasattr(self, 'parentGUI'):
                # this is executed for GUI redraws
                # delete everything inside the existing scrollable canvas
                _clearKids(self.parentGUI)
                _clearKids(self.prefFrame)
                canvas = self.canvas
                taskGUIframeInterior = self.taskGUIframeInterior
                interior_id = self.interior_id
                yscrollbar = self.yscrollbar
                prefFrame = self.prefFrame

            else:
                # this is executed at the first GUI creation
                # create an empty scrollable canvas
                top.grid_rowconfigure(0, weight=1)
                top.grid_columnconfigure(0, weight=1)
                self.yscrollbar = yscrollbar = ttk.Scrollbar(top)
                yscrollbar.grid(row=0, column=1, sticky=tk.N + tk.S + tk.W)
                self.canvas = canvas = tk.Canvas(top, bd=0, yscrollcommand=yscrollbar.set)
                canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
                yscrollbar.config(command=canvas.yview)
                self.taskGUIframeInterior = taskGUIframeInterior = ttk.Frame(canvas)
                taskGUIframeInterior.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
                self.interior_id = interior_id = canvas.create_window(0, 0, anchor=tk.NW, window=taskGUIframeInterior)
                self.parentGUI = taskGUIframeInterior

                # preference window
                self.prefFrame = prefFrame = ttk.Frame(top)
                prefFrame.grid(row=0, column=2, sticky=tk.N + tk.S)

                # mousewheel scroll on users GUI
                def mouse_wheel(event):
                    # respond to Linux or Windows wheel event
                    if event.num == 5 or event.delta == -120:
                        canvas.yview('scroll', 1, 'units')
                    if event.num == 4 or event.delta == 120:
                        canvas.yview('scroll', -1, 'units')
                    return 'break'

                top.bind("<MouseWheel>", mouse_wheel)
                top.bind("<Button-4>", mouse_wheel)
                top.bind("<Button-5>", mouse_wheel)

            taskGUIframeInterior.pack_propagate(0)

            # #add setupModule buttons
            # if self.relativeLocations['root'] is not OMFIT:
            #     try:
            #         _setupModule(prefFrame)
            #     except Exception as _excp:
            #         printe('Error in setupModule GUI: '+repr(_excp))

            # initialize things for compound GUIs, tabs, notebooks and configuration of sizes
            _aux['parentGUI'] = self.parentGUI
            _aux['is_compoundGUI'] = False
            _aux['notebook'] = None
            _aux['tab_name'] = ''
            _aux['tab_list'] = {}
            _aux['tab_list'][''] = _aux['parentGUI']
            _aux['configure_size'] = []
            old_same_row = _aux['same_row']
            _aux['same_row'] = None
            old_packing = _aux['packing']
            _aux['packing'] = tk.TOP
            _GUIs[str(_aux['topGUI'])].notebooks = {}
            _GUIs[str(_aux['topGUI'])].locked = []

            # header GUI
            headerGUI = self.kw.pop('headerGUI', '')
            if not isinstance(headerGUI, str):
                headerGUI = headerGUI.read()
            if headerGUI:
                self.kw['prerun'] = self.kw.get('prerun', '') + '\n' + headerGUI

            # footer GUI
            footerGUI = self.kw.pop('footerGUI', '')
            if not isinstance(footerGUI, str):
                footerGUI = footerGUI.read()
            if footerGUI:
                self.kw['postrun'] = self.kw.get('postrun', '') + '\n' + footerGUI

            # execute the main pythonGUI
            self.kw['compoundGUI'] = False
            self.pythonFile.__run__(**self.kw)

            _aux['same_row'] = old_same_row
            _aux['packing'] = old_packing

            # handle resizing
            def configure_size():
                canvas.unbind('<Configure>')
                canvas.update_idletasks()
                canvas.configure(scrollregion=(0, 0, top.winfo_width(), taskGUIframeInterior.winfo_reqheight()))
                GUIheight = min([taskGUIframeInterior.winfo_reqheight(), int(OMFITaux['rootGUI'].winfo_height() * 0.9)])
                GUIwidth = max(
                    [taskGUIframeInterior.winfo_reqwidth(), top.winfo_width() - yscrollbar.winfo_reqwidth() - prefFrame.winfo_reqwidth()]
                )
                canvas.itemconfigure(interior_id, width=GUIwidth, height=taskGUIframeInterior.winfo_reqheight())
                canvas.configure(width=GUIwidth, height=GUIheight)
                top.configure(width=GUIwidth + yscrollbar.winfo_reqwidth() + prefFrame.winfo_reqwidth(), height=GUIheight)
                for item, action in _aux['configure_size']:
                    try:
                        item.bind('<Configure>', lambda event: action())
                    except tk.TclError:
                        pass
                _aux['configure_size'] = []
                canvas.update_idletasks()
                canvas.bind('<Configure>', lambda event: configure_size())

            taskGUIframeInterior.pack_propagate(1)

            configure_size()

            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")

        except Exception:
            # if anything goes wrong close the GUI and raise the error
            _clearClosedGUI(self.top)
            raise


def _clearClosedGUI(top):
    """
    This method is used internally by OMFIT to clear the data of GUIs which have been closed by users

    :param top: TkInter ID of the closed GUI

    :return: None
    """
    if str(top) in _GUIs:
        del _GUIs[str(top)]
    try:
        _clearKids(top)
        top.destroy()
    except Exception:
        pass


def _clearKids(top):
    """
    Recursive cleanup of all elements under TkInter ID

    :param top: TkInter ID of the parent whose kids must be cleared

    :return: None
    """
    try:
        top.winfo_children()
    except Exception:
        return
    for kid in top.winfo_children():
        _clearKids(kid)
    for kid in top.winfo_children():
        try:
            kid.pack_forget()
        except Exception:
            pass
        kid.destroy()


def _absLocation(location):
    """
    This method is used internally by OMFIT to translate relative locations used
    in a OMFITpythonGUI script to absolute locations in the OMFIT tree.

    :param location: string with relative/absolute location in the OMFIT tree

    :return: absolute location string in the OMFIT tree
    """
    return absLocation(location, relativeLocations(_GUIs[str(_aux['topGUI'])].pythonFile), base_is_relativeLocations_output=True)


@_available_to_userGUI
def UpdateGUI(top=None):
    """
    Function used to update users GUIs

    :param top: TopLevel tk GUI to be updated
    """
    if top is None:
        topList = [_GUIs[k].top for k in list(_GUIs.keys())]
    else:
        topList = [top]
    for _aux['topGUI'] in topList:
        _GUIs[str(_aux['topGUI'])].update()


@_available_to_userGUI
def Refresh():
    '''
    Force a refresh of the OMFIT GUI by issuing a TkInter .update()
    '''
    if OMFITaux['GUI'] is not None and not len(OMFITaux['prun_process']):
        OMFITaux['console'].flush()


@_available_to_userGUI
def CloseAllGUIs():
    """
    Function for closing all users GUIs
    """
    for k in list(_GUIs.keys()):
        top = _GUIs[k].top
        _clearClosedGUI(top)


def _topGUI(item=None):
    """
    Function to reach the TopLevel tk from a GUI element

    :param item: tk GUI element

    :return: TopLevel tk GUI
    """
    if item is None:
        item = _aux['parentGUI']
    return TKtopGUI(item)


def _tk_ttk_process_kw(type, kw):
    '''
    converts tk configure attributes to ttk styles

    :param type: one of the ttk_styles

    :param kw: tk configure instructions

    :return: custom ttk style
    '''
    if not len(kw) or 'style' in kw:
        if 'style' in kw and type not in kw['style']:
            kw['style'] = kw['style'] + '.' + type
        return kw
    if 'fg' in kw:
        kw['foreground'] = kw.pop('fg')
    if 'bg' in kw:
        kw['background'] = kw.pop('bg')
    style_name = custom_ttk_style(type, **kw)
    kw.pop('foreground', None)
    kw.pop('background', None)
    kw['style'] = style_name
    return kw


def _ttk_tk_process_kw(kw):
    if 'foreground' in kw:
        kw['fg'] = kw.pop('foreground')
    return kw


# ---------------------------
# GUI elements
# ---------------------------
def _harvest_experiment_info(extra_info={}):
    '''
    harvest experiment info
    '''
    from omfit_classes.omfit_harvest import harvest_send

    project = OMFIT.prj_options
    for item in list(_aux['harvest'].keys()):
        if OMFIT.filename is not None and len(OMFIT.filename):
            if 'device' in _aux['harvest'][item]:
                _aux['harvest'][item]['_tag'] = tokamak(_aux['harvest'][item]['device'])
            for k in ['color', 'type', 'notes']:
                if k in project:
                    _aux['harvest'][item]['_' + k] = project[k]
            _aux['harvest'][item]['project'] = OMFIT.filename
            _aux['harvest'][item]['user'] = os.environ['USER']
            _aux['harvest'][item].update(extra_info)
            for k in _aux['harvest'][item]:
                try:
                    _aux['harvest'][item][k] = evalExpr(_aux['harvest'][item][k])
                except Exception:
                    printd('Error harvesting %s' % k, topic='harvest')
            host, port = evalExpr(SERVER['gadb-harvest']['HARVEST_server']).split(':')
            harvest_send(_aux['harvest'][item], 'omfit_experiment', host=host, protocol='UDP')
        del _aux['harvest'][item]


def _for_each_collection(location):
    loc = parseLocation(location)
    where = [loc.pop(0)]
    loc0 = buildLocation(where)
    for k in range(1, len(loc)):
        where += [loc.pop(0)]
        loc0 = buildLocation(where)
        if isinstance(eval(loc0), OMFITcollection) and loc[0] not in eval(loc0).KEYS():
            break
    if isinstance(eval(loc0), OMFITcollection):
        locs = []
        for k in eval(loc0).KEYS():
            locs.append(buildLocation(where + [k] + loc))
        return locs, True
    return location, False


def _setDefault(location, default=special1):
    """
    This method is used internally by OMFIT to set the default values of GUI elements

    :param location: location in the OMFIT tree (can be multiple locations)

    :param default: Default value (multiple defaults if multiple locations)

    :return: None
    """
    default_at_import = False
    if default is special1 and isinstance(location, str):
        try:
            default = eval(location.replace('SETTINGS', '__SETTINGS_AT_IMPORT__'))
            default_at_import = True
        except KeyError:
            pass

    if default is not special1 and not (
        not isinstance(location, str)
        and np.iterable(location)
        and np.iterable(default)
        and len(default)
        and next(default.__iter__()) is special1
    ):
        updated = False
        if isinstance(location, str):
            try:
                eval(location)
            except Exception:
                OMFIT.addBranchPath(location)
                eval(buildLocation(parseLocation(location)[:-1]))[parseLocation(location)[-1]] = default
                updated = True
        elif np.iterable(location):
            if len(location) != len(default):
                raise Exception('GUI error: Length of defaults must equal length of locations')
            for k, loc in enumerate(location):
                try:
                    eval(loc)
                except Exception:
                    OMFIT.addBranchPath(loc)
                    eval(buildLocation(parseLocation(loc)[:-1]))[parseLocation(loc)[-1]] = default[k]
                    updated = True
    return default, default_at_import


def _reveal(location=None, lbl=None, help=None):
    '''
    Reveals path/value of OMFIT GUI elements

    :param location: location (already pre-processed by _absLocation)

    :param lbl: human readeable description

    :param help: help
    '''
    if lbl is None:
        lbl = ''
    lbl = tolist(lbl)
    if isinstance(location, _OMFITpython):
        location = relativeLocations(location)
    elif callable(location):
        location_str = str(location)
        if '<lambda' in location_str:
            location_str = 'Calls lambda function defined as:\n' + inspect.getsource(location)
        if '<function' in location_str:
            location_str = 'Calls function defined as:\n' + inspect.getsource(location)
        location = location_str
    locations = tolist(location)
    lbls = lbl * len(locations)
    for lbl, location in zip(lbls, locations):
        loc = str(location)
        if OMFITcwd in loc:
            loc = os.path.split(loc)[1]
        value = ''
        if location.startswith('OMFIT['):
            try:
                if eval(location) is None or isinstance(eval(location), (int, float, str)):
                    value = ' = ' + repr(eval(location))
            except Exception:
                pass
        printi('* %s --> %s%s' % (lbl, loc, value))
    if help is not None and len(help):
        printi('== HELP ==')
        printi('  ' + '\n  '.join(help.split('\n')))


def _eval(location):
    '''
    Same as eval() but works also when location is a list of locations
    '''
    multiple = not isinstance(location, str)
    locations = np.atleast_1d(location).tolist()
    for k, location in enumerate(locations):
        locations[k] = eval(location)
    if multiple:
        return locations
    else:
        return locations[0]


def _Entry(
    parent,
    location,
    lbl=None,
    updateGUI=False,
    help='',
    preentry=None,
    postcommand=None,
    check=special1,
    collect=False,
    reveal_location=None,
    **kw,
):
    r"""
    Private method used to add entry GUI elements
    The background of the GUI gets colored green/red depending on whether the input by the user is a valid Python entry

    :param parent: parent TkInter object

    :param location: location in the OMFIT tree to be updated (it's a string)

    :param lbl: text on the left of the entry box

    :param updateGUI: whether the whole GUI should be redrawn when the value is updated

    :param help: string to be printed when the user right-clicks on the element

    :param preentry: function to pre-process the data at the OMFIT location to be displayed in the entry GUI element

    :param postcommand: function to post-process what the user has entered in the entry GUI element

    :param check: function that returns whether what the user has entered in the entry GUI element is a valid entry
                  This will make the background colored yellow, and users will not be able to set the value.

    :param \**kw: keywords passed to the ttk.Entry object

    :return: associated ttk.Entry object
    """
    from utils_widgets import OMFITfont

    kw = _tk_ttk_process_kw('TEntry', kw)
    value = tk.StringVar()
    oldValueRepr = dict(val=repr_eval(location, preentry, collect=collect))

    e = ttk.Entry(parent, textvariable=value, takefocus=False, **kw)
    e.configure(font=OMFITfont())
    e.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    value.set(repr_eval(location, preentry, collect=collect))

    if Lock(location, checkLock=True):
        e.config(state=tk.DISABLED)

    else:

        def set_location(location, tmp):
            if isinstance(eval(tmp), list) and isinstance(eval(location), np.ndarray) and len(eval(location).shape) == 1:
                tmp = 'np.atleast_1d(' + tmp + ')'
            exec(location + "=" + tmp, globals(), locals())

        def update_tree_values(location, updateGUI):
            tmp = checkKeyPressed()
            if tmp[0] is False:
                printe('Invalid Python entry: ' + value.get())
                return
            elif tmp[0] is None and tmp[1] is None:
                printe('Tree entry ' + location + ' should not be set as: ' + value.get())
                return
            elif tmp[0] is None:
                printe('Tree entry ' + location + ' should be ' + tmp[1])
                return
            # valid entry - lets use it
            tmp = value.get()
            e.state(['!invalid', '!alternate', '!active'])  # return style to default (remove color etc.)
            e.config(style='TEntry')
            if not isinstance(location, str):
                if len(tolist(eval(tmp))) > 1:
                    for k, loc in enumerate(location):
                        set_location(loc, tmp + "[%d]" % k)
                else:
                    for loc in location:
                        set_location(loc, tmp)
            else:
                set_location(location, tmp)
            oldValueRepr['val'] = repr_eval(location, preentry, collect=collect)
            if postcommand is not None:
                manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
            try:
                if isinstance(location, str):
                    eval(location)
            except KeyError:  # this is done to handle `delete_if_default` option or any post-command which deletes the entry
                pass
            else:
                oldValueRepr['val'] = repr_eval(location, preentry, collect=collect)
            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

        def checkKeyPressed():
            try:
                try:
                    tmp = repr_eval(value.get(), collect=collect)
                    if not tmp == oldValueRepr['val']:  # new value
                        if check is not special1:
                            if not check(_eval(tmp)):
                                e.state(['invalid', '!alternate', '!active'])
                                e.config(style='check.TEntry')
                            else:
                                e.state(['!invalid', '!alternate', 'active'])
                                e.config(style='valid.TEntry')
                        else:
                            e.state(['!invalid', '!alternate', 'active'])
                            e.config(style='valid.TEntry')
                    else:  # no change in value
                        e.state(['!invalid', '!alternate', '!active'])
                        e.config(style='TEntry')
                except Exception as _excp:
                    e.state(['alternate', '!invalid', '!active'])
                    e.config(style='error.TEntry')
                    # printe('Error: ' + repr(_excp) + '\nIs this a valid Python entry?\nDid you forget to add string quotations?')  # too much printing
                if e.instate(['alternate']):
                    return False, None
                elif e.instate(['invalid']):
                    tmp = None
                    if 'is_' == check.__name__[:3]:
                        tmp = check.__name__[3:]
                    return None, tmp
                else:
                    return True, None
            except Exception:
                pass

        def escape():
            value.set(oldValueRepr['val'])
            checkKeyPressed()

        if check is not special1:
            if not check(_eval(value.get())):
                e.config(background='goldenrod1')

        e.bind("<Return>", lambda event: update_tree_values(location, updateGUI))
        e.bind("<KP_Enter>", lambda event: update_tree_values(location, updateGUI))
        e.bind("<Key>", lambda event: e.after(1, checkKeyPressed))
        e.bind("<<virtualKey>>", lambda event: checkKeyPressed())
        e.bind("<Escape>", lambda event: e.after(1, escape))

    if reveal_location is None:
        reveal_location = location
    e.bind(f"<{rightClick}>", lambda event: _reveal(reveal_location, lbl, help))

    return e, value


def _Label(parent, lbl, **kw):
    """
    Private method used to add labels and comments

    :param parent: parent TkInter object

    :param lbl: text in the label

    :return: associated ttk.Label object
    """
    kw = _tk_ttk_process_kw('TLabel', kw)
    lbl = ttk.Label(parent, text=lbl, **kw)
    lbl.config(justify=tk.LEFT)
    return lbl


def _Text(parent, location, lbl=None, updateGUI=False, help='', preentry=None, postcommand=None, reveal_location=None, **kw):
    kw = _ttk_tk_process_kw(kw)
    top = tk.Toplevel(parent)
    top.transient(parent)
    top.wm_title(lbl)

    e = tk.ScrolledText(top, wrap=tk.NONE, undo=tk.TRUE, maxundo=-1, relief=tk.GROOVE, border=1, height=12, takefocus=False, **kw)
    e.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    if isinstance(eval(location), str):
        if preentry is None:
            e.set(eval(location))
        else:
            e.set(preentry(eval(location)))
    elif isinstance(eval(location), np.ndarray):
        if preentry is None:
            e.set(repr(eval(location)))
        else:
            e.set(repr(preentry(eval(location))))
    # allow line splitting of multi item lists in multiline edit option of Entry
    elif isinstance(eval(location), list):
        e.set(repr_eval(location, preentry).replace('],', '],\n'))
    else:
        e.set(repr_eval(location, preentry))

    if Lock(location, checkLock=True):
        e.config(state=tk.DISABLED)

    else:

        def update_tree_values(location, updateGUI):
            tmp = e.get()
            if isString.get():
                tmp = repr(tmp)
            else:
                if isinstance(eval(tmp), list) and isinstance(eval(location), np.ndarray) and len(eval(location).shape) == 1:
                    tmp = 'np.atleast_1d(' + tmp + ')'
            exec(location + "=" + tmp, globals(), locals())
            if postcommand is not None:
                manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
            top.destroy()

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        isString = tk.BooleanVar()
        if isinstance(eval(location), str):
            isString.set(True)
        ttk.Checkbutton(frm, text="is string", variable=isString, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, padx=5)
        update_button = ttk.Button(frm, text="Update", command=lambda: update_tree_values(location, updateGUI), takefocus=False)
        update_button.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5)

    top.bind("<Escape>", lambda event: top.destroy())

    if reveal_location is None:
        reveal_location = location
    e.bind(f"<{rightClick}>", lambda event: _reveal(reveal_location, lbl, help))

    return e


def _helpButton(master, help):
    if help:
        ttk.Button(
            master, text='?', command=lambda help=help: helpTip.showtip(help, move=False, strip=True), style='flat.TButton', takefocus=False
        ).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)


def _urlButton(master, url):
    if url:
        if '://' not in url:
            url = 'http://' + url
        ttk.Button(master, text='w', command=lambda url=url: openInBrowser(url), takefocus=False, style='flat.TButton').pack(
            side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0
        )


@_available_to_userGUI
def CompoundGUI(pythonFile, title=None, **kw):
    """
    This method allows the creation of nested GUI.

    :param pythonFile: is meant to be an OMFITpythonGUI object in the OMFIT tree

    :param title: title to appear in the compound GUI frame.
                  If None, the location of the `pythonFile` object in the OMFIT tree will be shown.
                  If an empty string, the compound GUI title is suppressed.

    :return: None
    """
    from omfit_classes.omfit_python import OMFITpythonGUI
    from utils_widgets import OMFITfont

    if isinstance(pythonFile, str):
        pythonFile = eval(pythonFile)
    if not isinstance(pythonFile, OMFITpythonGUI):
        raise Exception('GUI scripts must be declared as OMFITpythonGUI objects')

    tmp = _GUIs[str(_aux['topGUI'])].pythonFile
    tmp_parentGUI = (
        _aux['parentGUI'],
        _aux['notebook'],
        _aux['tab_name'],
        _aux['tab_list'],
        _aux['same_row'],
        _aux['packing'],
        _aux['compoundGUIid'],
    )

    try:
        _GUIs[str(_aux['topGUI'])].pythonFile = pythonFile

        bw = 2
        if title is not None and not len(title):
            bw = 0
        _aux['parentGUI'] = ttk.Frame(_aux['parentGUI'], borderwidth=bw, relief=tk.GROOVE)
        _aux['parentGUI'].pack(side=_aux['packing'], expand=tk.NO, fill=tk.BOTH, padx=bw, pady=bw)

        _aux['compoundGUIcounter'] += 1
        _aux['compoundGUIid'] += '(%d)@' % _aux['compoundGUIcounter'] + _aux['tab_name']
        _aux['same_row'] = None
        _aux['packing'] = tk.TOP
        _aux['notebook'] = None
        _aux['tab_name'] = ''
        _aux['tab_list'] = {}
        _aux['tab_list'][''] = _aux['parentGUI']

        if title is None:
            Label(treeLocation(_GUIs[str(_aux['topGUI'])].pythonFile)[-1], font=OMFITfont('bold', -2))
        elif len(title.strip()):
            Label(title, font=OMFITfont('bold', -2))

        tmp_is_compoundGUI = _aux['is_compoundGUI']
        _aux['is_compoundGUI'] = True
        kw.setdefault('compoundGUI', True)
        out_namespace = pythonFile.__run__(**kw)
        _aux['is_compoundGUI'] = tmp_is_compoundGUI

        return out_namespace

    finally:
        (
            _aux['parentGUI'],
            _aux['notebook'],
            _aux['tab_name'],
            _aux['tab_list'],
            _aux['same_row'],
            _aux['packing'],
            _aux['compoundGUIid'],
        ) = tmp_parentGUI
        _GUIs[str(_aux['topGUI'])].pythonFile = tmp


@_available_to_userGUI
def Tab(name=''):
    """
    This method creates a Tab under which the successive GUI elements will be placed

    :param name: Name to assign to the TAB

    :return: None
    """
    _aux['tab_name'] = name

    # if there was no notebook create one
    if _aux['notebook'] is None and len(name):
        _aux['notebook'] = ttk.Notebook(_aux['parentGUI'], takefocus=False)
        _aux['notebook'].pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        _GUIs[str(_aux['topGUI'])].notebooks[_aux['compoundGUIid']] = _aux['notebook']
    # if the name is not in the tab, then add it
    if name not in _aux['tab_list']:
        _aux['tab_list'][name] = ttk.Frame(_aux['notebook'])
        _aux['notebook'].add(_aux['tab_list'][name], text=name)
    # if there was a notebook, try to re-select the tabs which were selected
    if len(_aux['open_tabs']):
        try:
            _aux['notebook'].select(_aux['open_tabs'][_aux['compoundGUIid']])
            # printi(name,_aux['compoundGUIid'], _aux['open_tabs'][_aux['compoundGUIid']])
        except Exception as _excp:
            pass
            # printe(name,_aux['compoundGUIid'], _aux['open_tabs'][_aux['compoundGUIid']], repr(_excp))
    # activate the tab
    _aux['parentGUI'] = _aux['tab_list'][name]


@_available_to_userGUI
def Entry(
    location,
    lbl=None,
    comment=None,
    updateGUI=False,
    help='',
    preentry=None,
    postcommand=None,
    check=special1,
    multiline=False,
    norm=None,
    default=special1,
    delete_if_default=False,
    url='',
    kwlabel={},
    **kw,
):
    """
    This method creates a GUI element of the entry type
    The background of the GUI gets colored green/red depending on whether the input by the user is a valid Python entry

    :param location: location in the OMFIT tree (notice that this is a string)

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param preentry: function to pre-process the data at the OMFIT location to be displayed in the entry GUI element

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param check: function that returns whether what the user has entered in the entry GUI element is a valid entry.
                  This will make the background colored yellow, and users will not be able to set the value.

    :param default: Set the default value if the tree location does not exist (adds GUI button)

    :param delete_if_default: Delete tree entry if the value is the default value

    :param multiline: Force display of button for multiple-line text entry

    :param norm: normalizes numeric variables (overrides `preentry` or `postcommand`)

    :param url: open url in web-browser (adds GUI button)

    :param kwlabel: keywords passed to ttk.Label

    :return: associated ttk.Entry object
    """
    kwlabel = _tk_ttk_process_kw('TLabel', kwlabel)

    location = _absLocation(location)
    if isinstance(location, str):
        location, collection = _for_each_collection(location)
    multiple = not isinstance(location, str)
    if multiple:
        default = [default] * len(location)
    default, default_at_import = _setDefault(location, default)

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    if lbl is None:
        lbl = location
    ttk.Label(frm, text=str(lbl) + " = " * np.sign(len(str(lbl))), **kwlabel).pack(side=tk.LEFT)

    if norm is not None:

        def post(location, norm):
            exec(location + '*=' + str(norm), globals(), locals())

        def pre(value, norm):
            return value / norm

        preentry = lambda value, norm=norm: pre(value, norm)
        postcommand = lambda location, norm=norm: post(location, norm)

    if delete_if_default:
        postcommand = lambda location, postcommand=postcommand: delete_default(location, postcommand)

    e, value = _Entry(frm, location, lbl, updateGUI, help, preentry, postcommand, check=check, collect=multiple, **kw)

    # multiple entries
    if multiple:
        ttk.Label(frm, text='[%d]' % len(location), **kwlabel).pack(side=tk.LEFT)

    # multiline button
    elif multiline or isinstance(eval(location), str) and '\n' in eval(location):

        def showText():
            _Text(frm, location, lbl, True, help, preentry, postcommand, **kw)

        ttk.Button(frm, text="...", command=showText, takefocus=False, width=3).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=5)

    if not Lock(location, checkLock=True):
        # default button
        if default is not special1:

            def writeToEntry():
                e.focus_set()
                e.grab_set()
                value.set(repr(default))
                _aux['parentGUI'].update_idletasks()
                e.event_generate("<<virtualKey>>")
                e.grab_release()

            ttk.Button(
                frm,
                text=['d', 'D'][not default_at_import],
                command=writeToEntry,
                style='flat.TButton',
                takefocus=False,
                state=kw.get('state', 'enabled'),
            ).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)

    def delete_default(location, postcommand=None):
        if postcommand:
            postcommand()
        if eval(location) == default:
            exec(('del ' + location), globals(), locals())

    if delete_if_default:
        delete_default(location)

    return e


@_available_to_userGUI
def ComboBox(
    location,
    options,
    lbl=None,
    comment=None,
    updateGUI=False,
    state='readonly',
    help='',
    postcommand=None,
    check=special1,
    default=special1,
    url='',
    kwlabel={},
    **kw,
):
    """
    This method creates a GUI element of the combobox type.
    The background of the GUI gets colored green/red depending on whether the input by the user is a valid Python entry

    Notice that this method can be used to set multiple entries at once:
    `ComboBox(["root['asd']","root['dsa']","root['aaa']",],{'':[0,0,0],'a':[1,1,0],'b':[1,0,'***']},'Test multi',default=[0,0,0])`
    which comes very handy when complex/exclusive switch combinations need to be set in a namelist file, for example.
    Use the string `***` to leave parameters unchanged.

    :param location: location in the OMFIT tree (notice that this is either a string or a list of strings)

    :param options: possible options the user can choose from. This can be a list or a dictionary.

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param state: * 'readonly' (default) the user can not type in whatever he wants
                  * 'normal' allow user to type in
                  * 'search' allow searching for entries

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param check: function that returns whether what the user has entered in the entry GUI element is a valid entry.
                  This will make the background colored yellow, and users will not be able to set the value.

    :param default: Set the default value if the tree location does not exist (adds GUI button)

    :param url: open url in web-browser (adds GUI button)

    :param kwlabel: keywords passed to ttk.Label

    :return: associated TkInter combobox object
    """
    from utils_widgets import OMFITfont

    kwlabel = _tk_ttk_process_kw('TLabel', kwlabel)
    kw = _tk_ttk_process_kw('TEntry', kw)

    multiple = not isinstance(location, str)
    location = _absLocation(location)
    default, default_at_import = _setDefault(location, default)

    # escapeDescription will escape string options whose description matches the value
    def escapeDescription(description, value=None):
        description = str(description)
        if state == 'normal' and isinstance(value, str) and description == value and value != '':
            description = repr(description)
        return '***' + description + '***'

    # create key-text pair
    tmp = OrderedDict()
    if isinstance(options, (SortedDict, OrderedDict)):
        for key in list(options.keys()):
            tmp[escapeDescription(key, options[key])] = options[key]
    elif isinstance(options, dict):
        for key in sorted(list(options.keys()), key=str):
            tmp[escapeDescription(key, options[key])] = options[key]
    elif isinstance(options, (list, tuple)):
        for item in options:
            tmp[escapeDescription(item, item)] = item
    else:
        raise OMFITexception('ComboBox options can only be dictionaries, lists or tuples')
    options = tmp

    # handle wildcards
    # do not add wildcard entries if they have the same effective
    # value of an entry that does not have wildcards
    if multiple:
        for opt in list(options.keys()):
            modified = False
            tmp = copy.deepcopy(options[opt])
            for k, loc in enumerate(location):
                if tmp[k] == '***':
                    tmp[k] = eval(loc)
                    modified = True
            if modified:
                alreadyThere = False
                for opt1 in options:
                    if repr(options[opt1]) == repr(tmp):
                        alreadyThere = True
                if alreadyThere:
                    del options[opt]
                else:
                    options[opt] = tmp

    # create inverse lookup dictionary
    values = SortedDict()
    for description in options:
        values[repr(options[description])] = description

    # add also the current entry
    if repr(_eval(location)) not in values:
        options[escapeDescription(repr_eval(location), _eval(location))] = copy.deepcopy(_eval(location))
        values[repr_eval(location)] = escapeDescription(repr_eval(location), _eval(location))

    if lbl is None:
        lbl = location

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    ttk.Label(frm, text=lbl + " = " * np.sign(len(str(lbl))), **kwlabel).pack(side=tk.LEFT)
    comboBox = Combobox(
        frm,
        state=state if state != 'search' else 'normal',
        values=tuple([k.strip('*') for k in list(options.keys())]),
        takefocus=False,
        **kw,
    )
    comboBox.configure(font=OMFITfont())
    comboBox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
    comboBox.set(values[repr_eval(location)][3:-3])

    if Lock(location, checkLock=True):
        comboBox.config(state=tk.DISABLED)

    else:

        def update_tree_values(location, updateGUI):
            tmp = checkKeyPressed()
            if state == 'search':
                if escapeDescription(comboBox.get()) not in options:
                    escape()
                    return
            if tmp[0] is False:
                printe('Invalid Python entry: ' + comboBox.get())
                return
            elif tmp[0] is None and tmp[1] is None:
                printe('Tree entry ' + location + ' should not be set as: ' + comboBox.get())
                return
            elif tmp[0] is None:
                printe('Tree entry ' + location + ' should be ' + tmp[1])
                return

            if escapeDescription(comboBox.get()) in options:
                tmp = options[escapeDescription(comboBox.get())]
            else:
                tmp = _eval(comboBox.get())
            if isinstance(tmp, list) and isinstance(_eval(location), np.ndarray) and len(_eval(location).shape) == 1:
                tmp = np.atleast_1d(tmp)

            if isinstance(location, str):
                exec(location + '=' + repr(tmp), globals(), locals())
            else:
                for k, loc in enumerate(location):
                    exec(loc + '=' + repr(tmp) + '[k]', globals(), locals())

            if postcommand is not None:
                manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
            else:
                checkKeyPressed()

        def checkKeyPressed():
            # reorder entries based on matching search
            if state == 'search':
                try:
                    coptions = [x for x in comboBox.configure('values')[4] if x != '-----']
                except tk.TclError:
                    pass
                else:
                    tmp_options = []
                    for item in coptions:
                        if comboBox.get().lower() in item.lower():
                            tmp_options.append(item)
                    tmp_options.append('-----')
                    for item in coptions:
                        if comboBox.get().lower() not in item.lower():
                            tmp_options.append(item)
                    comboBox.configure(values=tuple(tmp_options))

            try:
                try:
                    # if the value is one of the options
                    if escapeDescription(comboBox.get()) in options:
                        if repr(options[escapeDescription(comboBox.get())]) == repr_eval(location):
                            comboBox.state(['active', '!invalid', '!alternate'])
                            comboBox.config(style='TCombobox')
                        else:
                            comboBox.state(['active', '!invalid', '!alternate'])
                            comboBox.config(style='valid.TCombobox')

                    # if in search mode
                    elif state == 'search':
                        comboBox.state(['active', '!invalid', '!alternate'])
                        comboBox.config(style='exist.TCombobox')
                        return True, 'search'

                    # if the value is not a valid option
                    else:
                        tmp = repr_eval(comboBox.get())
                        # if the value equals what's in the tree location (--> white)
                        if tmp == repr_eval(location):
                            comboBox.state(['!active', '!invalid', '!alternate'])
                            comboBox.config(style='TCombobox')

                        # if the value equals what's in the tree location (--> green)
                        else:
                            comboBox.state(['active', '!invalid', '!alternate'])
                            comboBox.config(style='valid.TCombobox')

                        # if there is a check and does not pass (--> orange)
                        if check is not special1 and not check(_eval(tmp)):
                            comboBox.state(['!active', 'invalid', '!alternate'])
                            comboBox.config(style='check.TCombobox')

                # if anything fails (--> red)
                except Exception as _excp:
                    comboBox.state(['!active', '!invalid', 'alternate'])
                    comboBox.config(style='error.TCombobox')

                if comboBox.instate(['alternate']):
                    return False, None
                elif comboBox.instate(['invalid']):
                    tmp = None
                    if 'is_' == check.__name__[:3]:
                        tmp = check.__name__[3:]
                    return None, tmp
                else:
                    return True, None
            except Exception:
                pass

        def escape():
            try:
                comboBox.set(values[repr_eval(location)][3:-3])
            except Exception:
                comboBox.set(repr_eval(location))
            checkKeyPressed()

        comboBox.bind('<<ComboboxSelected>>', lambda event: update_tree_values(location, updateGUI))
        comboBox.bind('<Return>', lambda event: update_tree_values(location, updateGUI))
        comboBox.bind('<KP_Enter>', lambda event: update_tree_values(location, updateGUI))
        comboBox.bind("<Key>", lambda event: comboBox.after(1, checkKeyPressed))
        comboBox.bind("<Escape>", lambda event: comboBox.after(1, escape))
        checkKeyPressed()

        # default button
        if default is not special1:

            def writeToEntry():
                if repr(default) in values:
                    comboBox.set(values[repr(default)][3:-3])
                elif state == 'normal':
                    comboBox.set(repr(default))
                else:
                    raise OMFITexception('Combobox %s: Default value %s is not a valid option' % (location, default))
                update_tree_values(location, updateGUI)
                checkKeyPressed()

            ttk.Button(
                frm,
                text=['d', 'D'][not default_at_import],
                command=writeToEntry,
                style='flat.TButton',
                takefocus=False,
                state=['enabled', 'disabled'][state == 'disabled'],
            ).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)

    comboBox.bind(f"<{rightClick}>", lambda event: _reveal(location, lbl, help))

    # break mousewheel scroll
    comboBox.bind("<MouseWheel>", 'break')
    comboBox.bind("<Button-4>", 'break')
    comboBox.bind("<Button-5>", 'break')

    return comboBox


@_available_to_userGUI
class same_row(object):
    '''
    Environment to place GUI elements on the same row

    For example to place two buttons side by side:

    >> with OMFITx.same_row():
    >>    OMFITx.Button('Run', lambda: None)
    >>    OMFITx.Button('Plot', lambda: None)
    '''

    def __enter__(self):
        self.frm_top = ttk.Frame(_aux['parentGUI'])
        self.old_aux = {}
        self.old_aux.update(_aux)
        _aux['same_row'] = _aux['parentGUI']
        _aux['parentGUI'] = self.frm_top
        _aux['packing'] = tk.LEFT
        return self

    def __exit__(self, type, value, traceback):
        _aux['packing'] = self.old_aux['packing']
        _aux['parentGUI'] = self.old_aux['parentGUI']
        _aux['same_row'] = self.old_aux['same_row']
        self.frm_top.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=0, pady=0)


@_available_to_userGUI
class same_tab(object):
    '''
    Environment to place GUI elements within the same tab

    For example to place two buttons in the same tab named 'test'

    >> with OMFITx.same_tab('test'):
    >>    OMFITx.Button('Run', lambda: None)
    >>    OMFITx.Button('Plot', lambda: None)
    '''

    def __init__(self, tab_name):
        self.tab_name = tab_name

    def __enter__(self):
        self.old_tab_name = _aux['tab_name']
        Tab(self.tab_name)
        return self

    def __exit__(self, type, value, traceback):
        Tab(self.old_tab_name)


@_available_to_userGUI
def Button(lbl, command, help='', url='', closeGUI=False, updateGUI=False, **kw):
    r"""
    This method creates a GUI element of the button type

    :param lbl: the text to be written on the button

    :param command: the command to be executed

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param url: open url in web-browser (adds GUI button)

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param closeGUI: Close current GUI after executing the command

    :param \**kw: extra keywords are passed to the ttk.Button

    :return: associated ttk.Button object
    """
    kw = _tk_ttk_process_kw('TButton', kw)

    reveal = command

    if isinstance(command, str):
        tmp = os.path.splitext(command)
        reveal = _absLocation(tmp[0]) + tmp[1]
        command = eval(reveal)

    if closeGUI:

        def command_and_close(current_gui, user_command):
            user_command()
            _clearClosedGUI(current_gui)

        command = lambda current_gui=_aux['topGUI'], user_command=command: command_and_close(current_gui, user_command)

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)

    def buttonClick(btt, command, updateGUI):
        btt.config(state=tk.DISABLED)
        try:
            command()
        finally:

            def back2normal(btt):
                try:
                    btt.config(state=tk.NORMAL)
                except Exception:
                    pass

            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
            else:
                btt.after(250, lambda: back2normal(btt))

    btt = ttk.Button(
        frm_top,
        text=lbl,
        command=lambda: buttonClick(btt, lambda: manage_user_errors(command, reportUsersErrorByEmail=True), updateGUI),
        takefocus=False,
        **kw,
    )
    btt.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    # help button
    _helpButton(frm_top, help)

    # web button
    _urlButton(frm_top, url)

    btt.bind(f"<{rightClick}>", lambda event: _reveal(reveal, lbl, help))
    return btt


@_available_to_userGUI
def Label(lbl, align='center', **kw):
    """
    This method creates a GUI element of the label type

    :param lbl: the text to be written in the label

    :param align: alignment of the text in the frame

    :return: associated ttk.Label object
    """
    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=tk.NO, fill=tk.X, padx=2, pady=2)

    image = kw.pop('image', None)
    if image is not None:
        try:
            im = tk.PhotoImage(master=frm_top, file=image)
        except tk.TclError:
            import PIL.ImageTk

            im = PIL.ImageTk.PhotoImage(master=frm_top, file=image)

    label = _Label(frm_top, lbl, **kw)

    if image is not None:
        label.configure(image=im)
        label._ntimage = im

    alignment = {'left': tk.LEFT, 'center': tk.TOP, 'right': tk.RIGHT}

    label.pack(side=alignment[align], expand=tk.NO, fill=tk.X)

    def robust_configure_size(event=None, label=label, frm_top=frm_top):
        try:
            label.config(wraplength=frm_top.winfo_width())
        except tk.TclError:
            pass

    _aux['configure_size'].append(
        (frm_top, lambda event=None, label=label, frm_top=frm_top: robust_configure_size(event=None, label=label, frm_top=frm_top))
    )
    return label


@_available_to_userGUI
def Separator(lbl=None, kwlabel={}, **kw):
    r"""
    This method creates a TkInter separator object

    :param lbl: text to be written between separator lines

    :param kwlabel: keywords passed to ttk.Label

    :param \**kw: keywords passed to ttk.Label

    :return: associated ttk.Label object
    """
    from utils_widgets import OMFITfont

    kwlabel.update(kw)
    if 'font' not in kwlabel:
        kwlabel['font'] = OMFITfont('bold')
    kwlabel = _tk_ttk_process_kw('TLabel', kwlabel)
    if not lbl:
        sep = ttk.Separator(_aux['parentGUI'])
        sep.pack(side=_aux['packing'], expand=tk.NO, fill=tk.X, padx=5, pady=2)
    else:
        frm_top = ttk.Frame(_aux['parentGUI'])
        frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=0, pady=0)
        ttk.Separator(frm_top).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=2)
        tmp = ttk.Label(frm_top, text=str(lbl), **kwlabel)
        tmp.pack(expand=tk.NO, fill=tk.NONE, side=tk.LEFT)
        ttk.Separator(frm_top).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=2)
        return tmp


@_available_to_userGUI
def FilePicker(
    location,
    lbl=None,
    comment=None,
    updateGUI=False,
    help='',
    postcommand=None,
    localRemote=True,
    transferRemoteFile=True,
    directory=False,
    action='open',
    tree=True,
    default=special1,
    url='',
    kwlabel={},
    init_directory_location=None,
    init_pattern_location=None,
    favorite_list_location=None,
    pattern_list_location=None,
    reveal_location=None,
    **kw,
):
    r"""
    This method creates a GUI element of the filePicker type, which allows to pick a file/directory

    :param location: location in the OMFIT tree (notice that this is a string)

    :param lbl: label to be shown near the button

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param localRemote: True: both, 'local': only local, 'remote': only remote

    :param transferRemoteFile: controls what goes into location

        * string with local filename (if transferRemoteFile==True)

        * string with the filename (if transferRemoteFile==False)

        * tuple with the filename,server,tunnel (if transferRemoteFile==None)

        if transferRemoteFile=True, then the file is transferred to a temporary folder

        if transferRemoteFile is a string, then it will be interpreted as the directory where to move the file

    :param directory: whether it's a directory or a file

    :param action: 'open' or 'save'

    :param tree: load from OMFIT tree location

    :param url: open url in web-browser (adds GUI button)

    :param kwlabel: keywords passed to ttk.Label

    :param init_directory_location: The contents of this location are used to set the initial directory for file searches.
                                    If a file name is specified the directory will be determined from the file name and this input ignored.
                                    Otherwise, if set this will be used to set the initial directory.

    :param init_pattern_location: The default pattern is '*'. If this is specified then the contents of the tree location will replace the default intial pattern.

    :param favorite_list_location: OMFIT tree location which contains a possibly empty list of favorite file directories. To keep with the general omfit approach this should be a string.

    :param pattern_list_location: OMFIT tree location which contains a possibly empty list of favorite search patterns. To keep with the general omfit approach this should be a string.

    :param reveal_location: location used for creation of the help (this is used internally by OMFIT, should not be used by users)

    :param \**kw: keywords passed to Entry object

    :return: associated ttk.Entry object
    """
    kwlabel = _tk_ttk_process_kw('TLabel', kwlabel)
    location = _absLocation(location)
    default, default_at_import = _setDefault(location, default)
    if reveal_location is None:
        reveal_location = location

    if action != 'open':
        transferRemoteFile = False
        localRemote = 'local'
        # todo: allow save to remote files

    def processFilename(tmp):
        exec(location + '=' + repr(tmp), globals(), locals())
        if postcommand is not None:
            manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
        value.set(repr(tmp))
        try:
            e.icursor(tk.END)
            e.xview(tk.END)
        except Exception:
            pass
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

    def askTree():
        top = tk.Toplevel(_topGUI(_aux['parentGUI']))
        top.withdraw()
        top.transient(_aux['parentGUI'])
        top.wm_title('Pick file tree location')

        _Label(top, 'Tree location: ').pack(side=tk.LEFT)
        var = tk.OneLineText(top, width=50, percolator=True)
        var.set(OMFITaux['GUI'].focusRoot)
        var.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.X, expand=tk.YES)

        def onReturn(var=None):
            if hasattr(eval(var.get()), 'filename') and eval(var.get()).filename:
                if hasattr(eval(var.get()), 'deploy'):
                    filename = tempfile._get_default_tempdir() + '/' + os.path.basename(eval(var.get()).filename)
                    eval(var.get()).deploy(filename)
                    processFilename(filename)
                    if os.path.isdir(filename):
                        shutil.rmtree(filename, ignore_errors=True)
                    else:
                        os.remove(filename)
                elif hasattr(eval(var.get()), 'save'):
                    eval(var.get()).save()
                    processFilename(eval(var.get()).filename)
                else:
                    printw(var.get() + " has no .deploy() or .save() methods! The chosen object may not be in sync.")
                    processFilename(eval(var.get()).filename)
            else:
                processFilename(var.get())
            top.destroy()

        def onEscape():
            top.destroy()

        var.focus_set()
        top.bind('<Return>', lambda event: onReturn(var=var))
        top.bind('<KP_Enter>', lambda event: onReturn(var=var))
        top.bind('<Escape>', lambda event: onEscape())

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        top.deiconify()
        top.wait_window(top)

    def askRemote():
        remoteFilename = None
        server = 'localhost'
        tunnel = ''
        try:
            tmp = eval(location)
        except Exception:
            pass
        else:
            if isinstance(tmp, str) and len(tmp):
                remoteFilename = tmp
            elif isinstance(tmp, (tuple, list, np.ndarray)) and len(tmp[0]):
                if len(tmp):
                    remoteFilename = tmp[0]
                if len(tmp) > 1:
                    server = tmp[1]
                if len(tmp) > 2:
                    tunnel = tmp[2]

        tmp = remoteFile(
            _aux['parentGUI'],
            transferRemoteFile,
            remoteFilename=remoteFilename,
            server=server,
            tunnel=tunnel,
            init_directory_location=init_directory_location,
            init_pattern_location=init_pattern_location,
            favorite_list_location=favorite_list_location,
            pattern_list_location=pattern_list_location,
            is_dir=directory,
        )
        if (isinstance(tmp, str) and len(tmp)) or (isinstance(tmp, (tuple, list, np.ndarray)) and len(tmp[0])):
            processFilename(tmp)

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, pady=1)

    if lbl is None:
        if not directory:
            lbl = 'Pick File'
        else:
            lbl = 'Pick Directory'

    ttk.Label(frm, text=str(lbl) + " = " * np.sign(len(str(lbl))), **kwlabel).pack(side=tk.LEFT)

    e, value = _Entry(
        frm, location=location, lbl=lbl, updateGUI=updateGUI, help=help, postcommand=postcommand, reveal_location=reveal_location, **kw
    )
    e.icursor(tk.END)
    e.xview(tk.END)
    e.config(width=30)

    bttTree = ttk.Button(frm, text='Tree', takefocus=False)
    if tree and (
        not localRemote or localRemote is True or localRemote == 'local' or (localRemote == 'remote' and transferRemoteFile is not False)
    ):
        bttTree.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
    bttTree.bind(f"<{rightClick}>", lambda event: _reveal(reveal_location, lbl, help))

    bttRemote = ttk.Button(frm, text=['File', 'Directory'][directory], takefocus=False)
    if localRemote:
        bttRemote.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
    bttRemote.bind(f"<{rightClick}>", lambda event: _reveal(reveal_location, lbl, help))

    if Lock(location, checkLock=True):
        bttTree.config(state=tk.DISABLED)
        bttRemote.config(state=tk.DISABLED)
    else:
        bttTree.config(command=askTree)
        bttRemote.config(command=askRemote)

        # default button
        if default is not special1:

            def writeToEntry():
                e.focus_set()
                e.grab_set()
                value.set(repr(default))
                _aux['parentGUI'].update_idletasks()
                e.event_generate("<<virtualKey>>")
                e.grab_release()

            ttk.Button(frm, text=['d', 'D'][not default_at_import], command=writeToEntry, style='flat.TButton', takefocus=False).pack(
                side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0
            )

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)

    return e


@_available_to_userGUI
def ObjectPicker(
    location,
    lbl=None,
    objectType=None,
    objectKW={},
    postcommand=None,
    unset_postcommand=None,
    kwlabel={},
    init_directory_location=None,
    init_pattern_location=None,
    favorite_list_location=None,
    pattern_list_location=None,
    **kw,
):
    r"""
    This helper method creates a GUI element of the objectPicker type, which allows to load objects in the tree.

    If an object is already present at the location, then a button allows picking of a different object.

    Notice that this GUI element will always call an updateGUI

    :param location: location in the OMFIT tree (notice that this is a string)

    :param lbl: label to be shown near the button/object picker

    :param objectType: class of the object that one wants to load (e.g. OMFITnamelist, OMFITgeqdsk, ...)
                       if `objectType is None` then the object selected with `Tree` is deepcopied

    :param objectKW: keywords passed to the object

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input.

    :param unset_postcommand: command to be executed after the value in the tree is deleted.  This command will receive the OMFIT location string as an input.

    :param kwlabel: keywords passed to ttk.Label

    :param init_directory_location: The contents of this location are used to set the initial directory for file searches.
                                    If a file name is specified the directory will be determined from the file name and this input ignored.
                                    Otherwise, if set this will be used to set the initial directory.

    :param init_pattern_location: The default pattern is '*'. If this is specified then the contents of the tree location will replace the default intial pattern.

    :param favorite_list_location: OMFIT tree location which contains a possibly empty list of favorite file directories. To keep with the general omfit approach this should be a string.

    :param pattern_list_location: OMFIT tree location which contains a possibly empty list of favorite search patterns. To keep with the general omfit approach this should be a string.

    :param \**kw: extra keywords are pased to the FilePicker object

    :return: associated ttk.Entry object
    """
    if isinstance(objectType, str):
        raise ValueError('ObjectPicker: object_type is not supposed to be a string')

    loc_orig = location
    location = _absLocation(location)

    locationObject = location
    locationScratch = _absLocation("scratch[" + repr('objectPicker_' + omfit_hash(location, 10)) + "]")

    tmp = parseLocation(location)
    where = eval(buildLocation(tmp[:-1]))
    what = tmp[-1]

    if objectType is None:
        kw['tree'] = True
        kw['localRemote'] = False

    def set(location=None):
        if objectType is None:
            where[what] = copy.deepcopy(eval(eval(locationScratch)))
        else:
            where[what] = objectType(eval(locationScratch), **objectKW)
        if postcommand is not None:
            manage_user_errors(lambda: postcommand(location=locationObject), reportUsersErrorByEmail=True)

    def unset():
        del where[what]
        if unset_postcommand is not None:
            manage_user_errors(lambda: unset_postcommand(location=locationObject), reportUsersErrorByEmail=True)

    if lbl is None:
        lbl = loc_orig

    if what in where:
        return Button('Pick a different ' + lbl, unset, updateGUI=True)

    else:
        kw.setdefault('default', '')
        kw.pop('updateGUI', None)
        kw.setdefault('transferRemoteFile', [True, None][isinstance(objectType, OMFITobject)])
        return FilePicker(
            locationScratch,
            "Pick " + lbl,
            postcommand=set,
            updateGUI=True,
            kwlabel=kwlabel,
            init_directory_location=init_directory_location,
            init_pattern_location=init_pattern_location,
            favorite_list_location=favorite_list_location,
            pattern_list_location=pattern_list_location,
            reveal_location=location,
            **kw,
        )


@_available_to_userGUI
def ModulePicker(location, modules=None, lbl=None, *args, **kw):
    r"""
    This method creates a GUI element of the combobox type for the selection of modules within the OMFIT project.

    :param location: location in the OMFIT tree (notice that this is either a string or a list of strings)

    :param modules: string or list of strings with IDs of the allowed modules. If modules is None all modules in OMFIT are listed

    :param lbl: label to be shown near the combobox

    :param load: list of two elements lists with module name and location where modules can be loaded
                 eg. [['OMFITprofiles',"root['OMFITprofiles']"],['EFIT',"OMFITmodules[-2]['EFIT']"],]
                 Setting `load=True` will set loading of the modules as submodules

    :param \*args: arguments passed to OMFITx.ComboBox

    :param \**kw: keywords passed to OMFITx.ComboBox

    :return: returns from OMFITx.ComboBox
    """

    if 'default' in kw:
        default, default_at_import = _setDefault(_absLocation(location), kw.pop('default'))

    try:
        existing_location = _absLocation(eval(_absLocation(location)))
    except Exception:
        existing_location = None

    options = {}

    modulesList = OMFIT.moduleDict()
    for module in modulesList:
        if modules is None or modulesList[module]['ID'] in tolist(modules):
            if 'OMFIT' + module == existing_location:
                options["[%s] -- %s" % (modulesList[module]['ID'], existing_location)] = eval(_absLocation(location))
            else:
                options["[%s] -- OMFIT%s" % (modulesList[module]['ID'], module)] = 'OMFIT' + module

    if kw.get('load', []) is True:
        kw['load'] = []
        for module in tolist(modules):
            kw['load'].append([module, "root['%s']" % module])
    if not kw.get('load', []):
        kw['load'] = []

    for m, l0cation in kw.pop('load', []):
        l0 = _absLocation(l0cation)
        try:
            eval(l0)
        except KeyError:
            options["load %s in %s" % (m, l0)] = '%s/%s' % (m, l0cation)

    if eval(_absLocation(location)) not in list(options.values()):
        options['--'] = eval(_absLocation(location))

    old_postcommand = kw.get('postcommand', None)

    def postcommand(location):
        if '/' in eval(_absLocation(location)):
            m, l = eval(_absLocation(location)).split('/')
            OMFIT.loadModule(m, _absLocation(l))
            exec('%s="%s"' % (location, l), globals(), locals())
            UpdateGUI()
        if old_postcommand is not None:
            old_postcommand(location)

    kw['postcommand'] = postcommand

    kw.setdefault('width', int(max([len(k) for k in list(options.keys())])))

    return ComboBox(location, options, lbl, *args, **kw)


@_available_to_userGUI
def TreeLocationPicker(
    location,
    lbl=None,
    comment=None,
    kwlabel={},
    default=special1,
    help='',
    url='',
    updateGUI=False,
    postcommand=None,
    check=None,
    base=None,
    **kw,
):
    r"""
    This method creates a GUI element used to select a tree location
    The label of the GUI turns green/red if the input by the user is a valid OMFIT tree entry (non existing tree entries are allowed)
    The label of the GUI turns green/red if the input by the user does or doesn't satisfy the `check` (non valid tree entries are NOT allowed)

    :param location: location in the OMFIT tree (notice that this is a string)

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param kwlabel: keywords passed to ttk.Label

    :param default: Set the default value if the tree location does not exist (adds GUI button)

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param url: open url in web-browser (adds GUI button)

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param check: function that returns whether what the user has entered in the entry GUI element is a valid entry
                  This will make the label colored yellow, and users will not be able to set the value.

    :param base: object in location with respect to which relative locations are evaluated

    :param \**kw: keywords passed to OneLineText object

    :return: associated ttk.Entry object
    """
    location = _absLocation(location)
    default, default_at_import = _setDefault(location, default)

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
    if lbl is None:
        lbl = location
    label = ttk.Label(frm, text=str(lbl), **kwlabel)
    label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
    ttk.Label(frm, text=" = " * np.sign(len(str(lbl))), **kwlabel).pack(side=tk.LEFT)

    kw.setdefault('percolator', True)
    kw.setdefault('width', 15)
    e = tk.OneLineText(frm, **kw)
    e.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
    e.set(eval(location))

    if Lock(location, checkLock=True):
        e.config(state=tk.DISABLED)

    else:

        def update_tree_values():
            tmp = checkKeyPressed()
            if check is None and tmp is False:
                printw(f'Location {e.get()} does not exist')
            elif tmp is None:
                printe(f'Location {e.get()} does not satisfy checks. Value not set. Press <ESC> to restore previous value.')
                return
            else:
                label.config(foreground='forestgreen')
            exec(location + "=" + repr(e.get()), globals(), locals())
            if postcommand is not None:
                manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

        def checkKeyPressed():
            if check is not None:
                try:
                    if not check(e.get()):
                        label.config(foreground='red2')
                        return None
                except Exception:
                    label.config(foreground='red2')
                    return None
                label.config(foreground='forestgreen')
                return True
            else:
                try:
                    if base is None:
                        tmp = _absLocation(e.get())
                    else:
                        tmp = absLocation(e.get(), base, False)
                    eval(tmp)  # check that the tree location exists
                    label.config(foreground='forestgreen')
                    return True
                except Exception as _excp:
                    label.config(foreground='red2')
                    return False

        def escape():
            e.set(eval(location))
            checkKeyPressed()

        def pickTree():
            e.set(OMFITaux['GUI'].focusRoot)
            update_tree_values()

        ttk.Button(frm, text='Tree', command=pickTree).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE)

        # default button
        if default is not special1:

            def writeToEntry():
                e.focus_set()
                e.grab_set()
                e.set(default)
                _aux['parentGUI'].update_idletasks()
                e.event_generate("<<virtualKey>>")
                e.grab_release()

            d = ttk.Button(frm, text=['d', 'D'][not default_at_import], command=writeToEntry, style='flat.TButton', takefocus=False)
            d.pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)

        e.bind("<Return>", lambda event: update_tree_values())
        e.bind("<KP_Enter>", lambda event: update_tree_values())
        e.bind("<Key>", lambda event: e.after(1, checkKeyPressed))
        e.bind("<<virtualKey>>", lambda event: checkKeyPressed())
        e.bind("<Escape>", lambda event: e.after(1, escape))

        checkKeyPressed()

    e.bind(f"<{rightClick}>", func=lambda event: _reveal(location, lbl, help))

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)


@_available_to_userGUI
def CheckBox(
    location,
    lbl=None,
    comment=None,
    useInt=False,
    mapFalseTrue=[],
    updateGUI=False,
    help='',
    postcommand=None,
    default=special1,
    url='',
    kwlabel={},
    **kw,
):
    r"""
    This method creates a GUI element of the checkbutton type

    This method accepts a list of locations, labels and defaults

    :param location: location in the OMFIT tree (notice that this is a string)

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param useInt: Use integers (1 or 0) instead of boolean (True or False)

    :param mapFalseTrue: a 2 elements list, the first one for the unchecked, the second one for the checked button

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param default: Set the default value if the tree location does not exist (adds GUI button)

    :param url: open url in web-browser (adds GUI button)

    :param kwlabel: keywords passed to ttk.Label

    :param \**kw: extra keywords are pased to the Checkbutton object

    :return: associated TkInter checkbutton object

    >>> OMFITx.CheckBox(["OMFIT['ck']","OMFIT['ck1']"],['hello','asd'],default=[False,True])
    >>> OMFITx.CheckBox("OMFIT['ck']",'hello',default=False)
    """

    kw.update(kwlabel)
    kw = _tk_ttk_process_kw('TCheckbutton', kw)

    location0 = location
    location = _absLocation(location)
    default, default_at_import = _setDefault(location, default)
    location = tolist(location)

    # define direct and inverse mappings
    if not len(mapFalseTrue):
        mapFalseTrue = [False, True]
        if useInt:
            mapFalseTrue = [0, 1]
    invMapFalseTrue = {repr(mapFalseTrue[0]): False, repr(mapFalseTrue[1]): True}

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)
    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

    if lbl is None:
        lbl = location
    lbl = tolist(lbl)

    # set the ticks
    e = []
    for k, loc in enumerate(location):
        e.append(ttk.Checkbutton(frm, text=str(lbl[k]), takefocus=False, **kw))
        e[k].pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        e[k].state(['!alternate'])
        if repr(eval(loc)) not in invMapFalseTrue:
            # color box bg indicating user that value is invalid with FalseTrue possibilities
            e[k].state(['alternate'])
        elif invMapFalseTrue[repr(eval(loc))]:
            e[k].state(['selected'])
        else:
            e[k].state(['!selected'])

    ttk.Frame(frm).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    if Lock(location, checkLock=True):
        for k in range(len(location)):
            e[k].config(state=tk.DISABLED)

    else:

        def update_tree_values(location, updateGUI, k):
            loc = location[k]
            if repr(eval(loc)) not in invMapFalseTrue:
                eloc = mapFalseTrue[1]
            else:
                eloc = mapFalseTrue[int(not invMapFalseTrue[repr(eval(loc))])]

            exec(loc + "=" + repr(eloc), globals(), locals())

            if postcommand is not None:  # pass the location of the item to postcommand
                manage_user_errors(lambda: postcommand(location=loc), reportUsersErrorByEmail=True)
            OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
            if updateGUI:
                OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

        for k, loc in enumerate(location):
            e[k].bind('<ButtonRelease-1>', lambda event, k=k: update_tree_values(location, updateGUI, k))

        # default button
        if default is not special1:

            def writeToEntry():
                for k, loc in enumerate(location):
                    exec(loc + "=" + repr(tolist(default)[k]), globals(), locals())
                if postcommand is not None:  # one single post-command when hitting `default`
                    loc = location
                    if len(loc) == 1:
                        loc = loc[0]
                    manage_user_errors(lambda: postcommand(location=loc), reportUsersErrorByEmail=True)
                for k, loc in enumerate(location):
                    if invMapFalseTrue.get(repr(eval(loc)), eval(loc)):
                        e[k].state(['selected'])
                    else:
                        e[k].state(['!selected'])

                OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
                if updateGUI:
                    OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

            ttk.Button(
                frm,
                text=['d', 'D'][not default_at_import],
                command=writeToEntry,
                style='flat.TButton',
                takefocus=False,
                state=kw.get('state', 'enabled'),
            ).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)

    for k, loc in enumerate(location):
        e[k].bind(f"<{rightClick}>", func=lambda event: _reveal(location, lbl, help))
    return e


@_available_to_userGUI
def ListEditor(
    location,
    options,
    lbl=None,
    default=None,
    unique=True,
    ordered=True,
    updateGUI=False,
    postcommand=None,
    only_valid_options=False,
    help='',
    url='',
    show_delete_button=False,
    max=None,
):
    '''
    GUI element to add or remove objects to a list
    Note: multiple items selection possible with the Shift and Ctrl keys

    :param location: location in the OMFIT tree (notice that this is a string).

    :param options: possible options the user can choose from. This can be a tree location, a list, or a dictionary.
                    If a dictinoary, then keys are shown in the GUI and values are set in the list.
                    In order to use "show_delete_button", this must be a string giving the location of a list in the tree.

    :param lbl: Label which is put on the left of the entry

    :param default: Set the default value if the tree location does not exist

    :param unique: Do not allow repetitions in the list

    :param ordered: Keep the same order as in the list of options
                    If false, then buttons to move elements up/down are shown

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param postcommand: function to be called after a button is pushed. It is called as postcommand(location=location,button=button) where button is in ['add','add_all','remove','remove_all']

    :param only_valid_options: list can only contain valid options

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param url: open url in web-browser (adds GUI button)

    :param show_delete_button: bool: Show an additional button for deleting items from the left hand list

    :param max: allow at most MAX choices

    '''
    if default is None:
        default = []

    location = _absLocation(location)
    default, default_at_import = _setDefault(location, default)

    if isinstance(options, str):
        options = _absLocation(options)
        if unique:
            eval(options)[:] = unsorted_unique(eval(options))
        opts = eval(options)

    elif isinstance(options, dict):
        opts = list(options.keys())
        reversed_options = flip_values_and_keys(options)

    else:
        if unique:
            options = unsorted_unique(options)
        opts = options

    if unique:
        eval(location)[:] = unsorted_unique(eval(location))

    if lbl is None:
        lbl = location

    if only_valid_options:
        for item in set(eval(location)).difference(set(opts)):
            eval(location).remove(item)

    selects = eval(location)

    if not isinstance(selects, list):
        raise Exception('%s: OMFITx.ListEditor works only with lists' % location)

    def post(button):
        if postcommand is not None:
            manage_user_errors(lambda: postcommand(location=location, button=button), reportUsersErrorByEmail=True)

    def add():
        # the GUI
        ixs = olx.curselection()
        if not ixs:
            return
        items = [opts[int(item)] for item in ixs]
        # the tree elements
        for item in items:
            if isinstance(options, dict):
                item = options[item]
            if not unique or item not in selects:
                selects.append(item)
        if max is not None and len(selects) > max:
            for n in range(len(selects) - max):
                selects.pop(0)
        if ordered:
            if isinstance(options, dict):
                selects.sort(key=lambda x: list(options.values()).index(x))
            else:
                selects.sort(key=lambda x: opts.index(x))
        # the GUI
        slx.delete(0, tk.END)
        for item in selects:
            if isinstance(options, dict):
                item = reversed_options.get(item, item)
            slx.insert(tk.END, item)
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        post('add')

    def add_all():
        # the tree elements
        if isinstance(options, dict):
            selects[:] = list(options.values())
        else:
            selects[:] = opts
        # the GUI
        slx.delete(0, tk.END)
        for item in selects:
            if isinstance(options, dict):
                item = reversed_options.get(item, item)
            slx.insert(tk.END, item)
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        post('add_all')

    def remove():
        # the GUI
        ixs = slx.curselection()
        if not ixs:
            return
        ixs = list(map(int, ixs))
        for k in sorted(ixs)[::-1]:
            slx.delete(k)
            selects.pop(k)
        # the tree elements
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        post('remove')

    def remove_all():
        # the GUI
        slx.delete(0, tk.END)
        selects[:] = []
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        post('remove_all')

    def delete_item():
        # Update list editor GUI
        ixs = olx.curselection()
        if not ixs:  # Nothing is selected
            if slx.curselection():
                print('Delete removes items from the left hand list; please select from the left list.')
            return
        ixs = list(map(int, ixs))
        for k in sorted(ixs)[::-1]:
            slx.delete(k)
            j = np.where(np.array(selects) == opts[k])[0]
            if len(j):
                olx.delete(j[0])
                selects.pop(j[0])
            opts.pop(k)
        # Update the tree elements
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        post('delete_item')

    def ud(direction):
        ixs = slx.curselection()
        if not ixs:  # Nothing is selected
            if slx.curselection():
                print('Delete removes items from the left hand list; please select from the left list.')
            return
        ixs = ixs[0]
        if direction == 'u' and (ixs - 1) >= 0:
            selects.insert(ixs - 1, selects.pop(ixs))
        elif direction == 'd' and (ixs + 1) < len(selects):
            selects.insert(ixs + 1, selects.pop(ixs))
        else:
            return
        slx.delete(0, tk.END)
        for item in selects:
            if isinstance(options, dict):
                item = reversed_options.get(item, item)
            slx.insert(tk.END, item)
        # the tree elements
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        if direction == 'u':
            slx.select_set(ixs - 1)
            slx.see(ixs - 1)
        else:
            slx.select_set(ixs + 1)
            slx.see(ixs + 1)

    top = ttk.Frame(_aux['parentGUI'])
    top.pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=1)

    frm = ttk.Frame(top)
    frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    scrollbaro = ttk.Scrollbar(frm)
    scrollbaro.pack(side=tk.RIGHT, fill=tk.Y)
    olx = tk.Listbox(frm, selectmode=tk.EXTENDED)
    olx.config(yscrollcommand=scrollbaro.set)
    scrollbaro.config(command=olx.yview)
    olx.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    for item in opts:
        olx.insert(tk.END, item)

    frm = ttk.Frame(top)
    frm.pack(side=tk.LEFT)
    bt = ttk.Label(frm, text=lbl)
    bt.pack(side=tk.TOP, fill=tk.X)

    frm1 = ttk.Frame(frm)
    frm1.pack(side=tk.TOP)
    # help button
    _helpButton(frm1, help)
    # web button
    _urlButton(frm1, url)

    bt = ttk.Label(frm, text='')
    bt.pack(side=tk.TOP, fill=tk.X)
    bt = ttk.Button(frm, text='Add >', command=add, takefocus=False)
    bt.pack(side=tk.TOP, fill=tk.X)
    if max is None:
        bt = ttk.Button(frm, text='Add all >>', command=add_all, takefocus=False)
        bt.pack(side=tk.TOP, fill=tk.X)

    frmm = ttk.Frame(frm)
    frmm.pack(side=tk.TOP, fill=tk.X)
    btxu = ttk.Button(frmm, text='up', command=lambda: ud('u'), takefocus=False, width=5)
    if not ordered:
        btxu.pack(side=tk.LEFT, expand=tk.NO, padx=0)
    ttk.Label(frmm, text='').pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
    btxd = ttk.Button(frmm, text='down', command=lambda: ud('d'), takefocus=False, width=5)
    if not ordered:
        btxd.pack(side=tk.LEFT, expand=tk.NO, padx=0)

    bt.pack(side=tk.TOP, fill=tk.X)
    bt = ttk.Button(frm, text='Remove <', command=remove, takefocus=False)
    bt.pack(side=tk.TOP, fill=tk.X)
    if max is None or max > 1:
        bt = ttk.Button(frm, text='Remove all <<', command=remove_all, takefocus=False)
        bt.pack(side=tk.TOP, fill=tk.X)
    if show_delete_button and isinstance(options, str):
        bt = ttk.Label(frm, text='')
        bt.pack(side=tk.TOP, fill=tk.X)
        bt = ttk.Button(frm, text='Delete', command=delete_item, takefocus=False)
        bt.pack(side=tk.TOP, fill=tk.X)

    frm = ttk.Frame(top)
    frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    scrollbarx = ttk.Scrollbar(frm)
    scrollbarx.pack(side=tk.LEFT, fill=tk.Y)
    slx = tk.Listbox(frm, selectmode=tk.EXTENDED)
    slx.config(yscrollcommand=scrollbarx.set)
    scrollbarx.config(command=slx.yview)
    slx.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    for item in selects:
        if isinstance(options, dict):
            item = reversed_options.get(item, item)
        slx.insert(tk.END, item)

    def mouse_wheel(event, what):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            what.yview('scroll', 1, 'units')
        elif event.num == 4 or event.delta == 120:
            what.yview('scroll', -1, 'units')
        return 'break'

    for k in ["<Button-4>", "<Button-5>", "<MouseWheel>"]:
        olx.bind(k, lambda event, what=olx: mouse_wheel(event, what))
        slx.bind(k, lambda event, what=slx: mouse_wheel(event, what))

    olx.bind(f"<{rightClick}>", lambda event: _reveal(location, lbl, help))
    slx.bind(f"<{rightClick}>", lambda event: _reveal(location, lbl, help))

    return olx, slx


@_available_to_userGUI
def Slider(
    location,
    start_stop_step,
    lbl=None,
    comment=None,
    digits=None,
    updateGUI=False,
    help='',
    preentry=None,
    postcommand=None,
    norm=None,
    default=special1,
    url='',
    kwlabel={},
    **kw,
):
    """
    This method creates a GUI element of the slider type

    :param location: location in the OMFIT tree (notice that this is a string)

    :param start_stop_step: list of tree elements with start/stop/step of the slider

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param digits: How many digits to use (if None uses 3 digits if start_stop_step has floats or else 0 digits if these are integers)

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param preentry: function to pre-process the data at the OMFIT location to be displayed in the entry GUI element

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param default: Set the default value if the tree location does not exist (adds GUI button)

    :param norm: normalizes numeric variables (overrides `preentry` or `postcommand`)

    :param url: open url in web-browser (adds GUI button)

    :param kwlabel: keywords passed to ttk.Label

    :return: associated TtkScale object
    """
    collect = False
    kwlabel = _tk_ttk_process_kw('TLabel', kwlabel)

    location = _absLocation(location)
    if isinstance(location, str):
        location, collection = _for_each_collection(location)
    default, default_at_import = _setDefault(location, default)

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    if lbl is None:
        lbl = location
    ttk.Label(frm, text=str(lbl) + " = " * np.sign(len(str(lbl))), **kwlabel).pack(side=tk.LEFT)

    if norm is not None:

        def post(location, norm):
            exec(location + '*=' + str(norm), globals(), locals())

        def pre(value, norm):
            return value / norm

        preentry = lambda value, norm=norm: pre(value, norm)
        postcommand = lambda location, norm=norm: post(location, norm)

    kw = _tk_ttk_process_kw('Horizontal.TScale', kw)

    def set_location(location, val):
        if isinstance(eval(val), list) and isinstance(eval(location), np.ndarray) and len(eval(location).shape) == 1:
            val = 'np.atleast_1d(' + val + ')'
        exec(location + "=" + val, globals(), locals())

    def update_tree_values(location, val, updateGUI):
        set_location(location, val)
        if postcommand is not None:
            manage_user_errors(lambda: postcommand(location=location), reportUsersErrorByEmail=True)
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
        if updateGUI:
            OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

    alarm = [None]

    def command(val):
        if alarm[0] is not None:
            OMFITaux['rootGUI'].after_cancel(alarm[0])
            alarm[0] = None
        alarm[0] = OMFITaux['rootGUI'].after(500, lambda: update_tree_values(location, val, updateGUI))

    e = TtkScale(
        frm,
        from_=start_stop_step[0],
        to=start_stop_step[1],
        tickinterval=start_stop_step[2],
        value=eval(location),
        digits=digits,
        command=command,
        **kw,
    )
    # e.after(500, command)
    e.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    if Lock(location, checkLock=True):
        e.scale.configure(state=tk.DISABLED)

    e.bind(f"<{rightClick}>", lambda event: _reveal(location, lbl, help))
    # e.bind("<ButtonRelease-1>", command)
    if not Lock(location, checkLock=True):
        # default button
        if default is not special1:

            def writeToEntry():
                e.scale.set(default)
                e.on_configure(None)
                _aux['parentGUI'].update_idletasks()

            ttk.Button(
                frm,
                text=['d', 'D'][not default_at_import],
                command=writeToEntry,
                style='flat.TButton',
                takefocus=False,
                state=kw.get('state', 'enabled'),
            ).pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=0, pady=0)

    # help button
    _helpButton(frm, help)

    # web button
    _urlButton(frm, url)

    return e


@_available_to_userGUI
def Lock(location, value=special1, checkLock=False, clear=False):
    """
    The lock method prevents users from using a GUI element which would affect a specific location in the OMFIT tree

    :param location: location in the OMFIT tree (notice that this is a string or a list of strings)
                     If location is None, then all locks are cleared.

    :param checkLock: False=set the lock | True=return the lock value

    :param value: lock location at this value

    :param clear: clear or set the lock

    :return: None if checkLock=False, otherwise True/False depending on value of the lock
    """
    multiple = not isinstance(location, str)
    locations = np.atleast_1d(location).tolist()
    for k, location in enumerate(locations):

        if checkLock:
            location = _absLocation(location)
            locations[k] = location in _GUIs[str(_aux['topGUI'])].locked
        elif location is None:
            _GUIs[str(_aux['topGUI'])].locked = []
        else:
            location = _absLocation(location)
            if not clear:
                _GUIs[str(_aux['topGUI'])].locked.append(location)
                if value is not special1:
                    tmp = parseLocation(location)
                    if multiple:
                        eval(buildLocation(tmp[:-1]))[tmp[-1]] = value[k]
                    else:
                        eval(buildLocation(tmp[:-1]))[tmp[-1]] = value
            elif location in _GUIs[str(_aux['topGUI'])].locked:
                _GUIs[str(_aux['topGUI'])].locked.remove(location)

    if checkLock:
        return np.all(locations)


@_available_to_userGUI
def TitleGUI(title=None):
    '''
    Sets the title to the user gui window (if it's not a compound GUI)

    :param title:  string containing the title

    :return: None
    '''
    if not _aux['is_compoundGUI']:
        _aux['topGUI'].wm_title(title)


@_available_to_userGUI
def ShotTimeDevice(
    postcommand=None,
    showDevice=True,
    showShot=True,
    showTime=True,
    showRunID=False,
    multiShots=False,
    multiTimes=False,
    showSingleTime=False,
    checkDevice=None,
    checkShot=None,
    checkTime=None,
    checkRunID=None,
    subMillisecondTime=False,
    stopIfNotSet=True,
    updateGUI=True,
):
    '''
    This high level GUI allows setting of DEVICE/SHOT/TIME of each module
    (sets up OMFIT MainSettings if root['SETTINGS']['EXPERIMENT']['XXX'] is an expression)

    :param postcommand: command to be executed every time device,shot,time are changed (location is passed to postcommand)

    :param showDevice: True/False show device section or list of suggested devices

    :param showShot: True/False show shot section or list with list of suggested shots

    :param showTime: True/False show time section or list with list of suggested times

    :param showRunID: True/False show runID Entry

    :param multiShots: True/False show single/multi shots

    :param multiTimes: True/False show single/multi times

    :param showSingleTime: True/False if multiTimes, still show single time

    :param checkDevice: check if device user input satisfies condition

    :param checkShot: check if shot user input satisfies condition

    :param checkTime: check if time user input satisfies condition

    :param checkRunID:  check if runID  user input satisfies condition

    :param subMillisecondTime: Allow floats as times

    :param stopIfNotSet: Stop GUI visualization if shot/time/device are not set

    :return: None
    '''

    if not np.any(
        [
            True if np.iterable(showDevice) else showDevice,
            True if np.iterable(showShot) else showShot,
            True if np.iterable(showTime) else showTime,
        ]
    ):
        return

    tmp = relativeLocations(_GUIs[str(_aux['topGUI'])].pythonFile)
    root = module = tmp['root']
    rootName = moduleName = tmp['rootName']

    tmp = parseLocation(rootName)
    OMFITlocationName = [buildLocation(tmp[: k + 1]) for k, item in enumerate(tmp)]

    OMFITmodulesName = []
    for tmpName in OMFITlocationName:
        if eval(tmpName).__class__ is OMFITmodule and tmpName != 'OMFIT':
            OMFITmodulesName.append(tmpName)
    OMFITmodules = list(map(eval, OMFITmodulesName))

    MainSettings = OMFIT['MainSettings']

    # point to root['SETTINGS']['EXPERIMENT'][xx] if root['SETTINGS']['EXPERIMENT'][xx] is not an expression
    # else point to MainSettings['EXPERIMENT'][xx]
    linked = 'linked'
    for item in ['device', 'shot', 'time', 'runid', 'shots', 'times']:
        if item in root['SETTINGS']['EXPERIMENT']:
            if not isinstance(root['SETTINGS']['EXPERIMENT'][item], OMFITexpression):
                linked = 'unlinked'
                break

    # point to root['SETTINGS']['EXPERIMENT'][xx]
    # if root['SETTINGS']['EXPERIMENT'][xx] is not an expression
    # else point to MainSettings['EXPERIMENT'][xx]
    exp = {}
    for item in ['device', 'shot', 'time', 'runid', 'shots', 'times']:
        if item in root['SETTINGS']['EXPERIMENT']:
            exp[item] = root['SETTINGS']['EXPERIMENT'][item]
            exp['%s_location' % item] = f"{treeLocation(root)[-1]}['SETTINGS']['EXPERIMENT']"
            for moduleName in reversed(OMFITmodulesName):
                module = eval(moduleName)
                if not isinstance(module['SETTINGS']['EXPERIMENT'][item], OMFITexpression):
                    exp[item] = module['SETTINGS']['EXPERIMENT'][item]
                    exp['%s_location' % item] = moduleName + "['SETTINGS']['EXPERIMENT']"
                    break

    if not is_none(MainSettings['EXPERIMENT']['shots']) and not np.iterable(MainSettings['EXPERIMENT']['shots']):
        MainSettings['EXPERIMENT']['shots'] = np.atleast_1d(MainSettings['EXPERIMENT']['shots'])
    if not is_none(eval(exp['shots_location'])['shots']) and not isinstance(eval(exp['shots_location'])['shots'], np.ndarray):
        exec(exp['shots_location'] + "['shots']=np.atleast_1d(" + exp['shots_location'] + "['shots'])", globals(), locals())

    if not is_none(MainSettings['EXPERIMENT']['times']) and not np.iterable(MainSettings['EXPERIMENT']['times']):
        MainSettings['EXPERIMENT']['times'] = np.atleast_1d(MainSettings['EXPERIMENT']['times'])
    if not is_none(eval(exp['shots_location'])['times']) and not isinstance(eval(exp['times_location'])['times'], np.ndarray):
        exec(exp['times_location'] + "['times']=np.atleast_1d(" + exp['times_location'] + "['times'])", globals(), locals())

    def postcommandArray(location=None):
        exec(location + "=np.unique(np.atleast_1d(" + location + "))", globals(), locals())
        return postcommand_mainsettings(location)

    def postcommand_mainsettings(location):
        MainSettings['EXPERIMENT'][parseLocation(location)[-1]] = evalExpr(eval(location))
        if postcommand is not None:
            return postcommand(location)

    oldParent = _aux['parentGUI']
    frm = ttk.Frame(oldParent)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    _aux['parentGUI'] = ttk.Frame(frm)
    _aux['parentGUI'].pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

    set_values = {}

    if np.iterable(showDevice) or showDevice:

        def checkDeviceFunction(inv):
            if isinstance(inv, str) and is_device(inv, 'NSTX') and eval(exp['shot_location'] + "['shot']") >= 200000:
                printe('NSTX shot must be < 200000')
            if isinstance(inv, str) and is_device(inv, 'NSTX-U') and eval(exp['shot_location'] + "['shot']") < 200000:
                printe('NSTX-U shot must be >= 200000')

            if checkDevice is None:
                return isinstance(inv, str)
            else:
                return isinstance(inv, str) and checkDevice(inv)

        if np.iterable(showDevice):
            deviceList = tolist(showDevice)
        else:
            deviceList = list(OMFIT['shotBookmarks'].keys())
        deviceList = list(np.unique(deviceList))
        ComboBox(
            exp['device_location'] + "['device']",
            deviceList,
            'Device',
            state=tk.NORMAL,
            updateGUI=updateGUI,
            postcommand=postcommand_mainsettings,
            check=checkDeviceFunction,
        )
        set_values['device'] = eval(exp['device_location'] + "['device']")

    if np.iterable(showShot) or showShot:
        if not multiShots:
            if np.iterable(showShot):
                shotList = list(np.unique(tolist(showShot)))
            else:
                try:
                    shotList = list(map(int, sorted(OMFIT['shotBookmarks'][device].keys())))
                except Exception:
                    shotList = []

            def checkShotFunction(inv):
                if checkShot is None:

                    def checkShot_fun(inv):
                        try:
                            shot = int(inv)
                        except ValueError:
                            print(f'{inv} is not int')
                            return False
                        else:
                            if is_device(eval(exp['device_location'] + "['device']"), 'NSTX') and shot >= 200000:
                                printe('NSTX shots must be < 200000')
                                return False
                            if is_device(eval(exp['device_location'] + "['device']"), 'NSTXU') and shot < 200000:
                                printe('NSTX-U shots must be >= 200000')
                                return False
                            return True

                else:
                    checkShot_fun = checkShot
                return is_int(inv) and checkShot_fun(inv)

            ComboBox(
                exp['shot_location'] + "['shot']",
                shotList,
                'Shot',
                state=tk.NORMAL,
                updateGUI=updateGUI,
                postcommand=postcommand_mainsettings,
                check=checkShotFunction,
            )
            set_values['shot'] = eval(exp['shot_location'] + "['shot']")
        else:

            def checkShotsFunction(inv):
                if checkShot is None:
                    return is_int_array(inv)
                else:
                    return is_int_array(inv) and checkShot(inv)

            Entry(
                exp['shots_location'] + "['shots']",
                'Shots',
                updateGUI=updateGUI,
                postcommand=postcommandArray,
                check=checkShotsFunction,
                multiline=True,
            )
            set_values['shots'] = eval(exp['shots_location'] + "['shots']")

    if np.iterable(showTime) or showTime:
        if multiTimes:

            def checkTimesFunction(inv):
                if subMillisecondTime:
                    if checkTime is None:
                        valid = is_array(inv)
                    else:
                        valid = is_array(inv) and checkTime(inv)
                else:
                    if checkTime is None:
                        valid = is_int_array(inv)
                    else:
                        valid = is_int_array(inv) and checkTime(inv)
                if valid:
                    return np.all(np.diff(inv) > 0)

            Entry(
                exp['times_location'] + "['times']",
                'Times' + ' [ms]',
                updateGUI=updateGUI,
                postcommand=postcommandArray,
                check=checkTimesFunction,
                multiline=True,
                help='Enter list of monotonically increasing times for analysis.\nAccepts python statements.\n'
                'Example: Enter\n    arange(start,stop,step)\nfor a uniform time base.\n\nIt may be useful to start with a smaller '
                'subset of times to get a feel for what is needed, then change to the full set of desired times.',
            )
            set_values['times'] = eval(exp['times_location'] + "['times']")
        if (multiTimes and showSingleTime) or not multiTimes:
            if np.iterable(showTime):
                timeList = list(np.unique(tolist(showTime)))
            else:
                try:
                    timeList = list(map(int, sorted(OMFIT['shotBookmarks'][device][str(shot)].keys())))
                except Exception:
                    timeList = []

            def checkTimeFunction(inv):
                if subMillisecondTime:
                    if checkTime is None:
                        return is_numeric(inv)
                    else:
                        return is_numeric(inv) and checkTime(inv)
                else:
                    if checkTime is None:
                        return is_int(inv)
                    else:
                        return is_int(inv) and checkTime(inv)

            ComboBox(
                exp['time_location'] + "['time']",
                timeList,
                'Time' + ' [ms]',
                state=tk.NORMAL,
                updateGUI=updateGUI,
                postcommand=postcommand_mainsettings,
                check=checkTimeFunction,
            )
            set_values['time'] = eval(exp['time_location'] + "['time']")

    if showRunID:
        Entry(
            exp['runid_location'] + "['runid']", 'run-ID', updateGUI=updateGUI, postcommand=postcommand_mainsettings, check=is_alphanumeric
        )

    def addBookmarks(device, shot, time, description=''):
        if device != None:
            OMFIT['shotBookmarks'].setdefault(device, namelist.NamelistName())
            if device != None and shot != None:
                OMFIT['shotBookmarks'][device].setdefault(str(shot), namelist.NamelistName())
                if device != None and shot != None and time != None:
                    if not description and str(time) in OMFIT['shotBookmarks'][device][str(shot)]:
                        del OMFIT['shotBookmarks'][device][str(shot)][str(time)]
                        printi('Deleted bookmark for %s #%s @ %s' % (device, str(shot), str(time)))
                    elif description:
                        OMFIT['shotBookmarks'][device][str(shot)][str(time)] = description
                else:
                    printi('Bookmarks: no time')
            else:
                printi('Bookmarks: no shot')
        else:
            printi('Bookmarks: no device')
        OMFIT['shotBookmarks'].save()

    def addBookmarksWithDescription(device, shot, time):
        def onEscape(location=None):
            top.destroy()

        top = tk.Toplevel(_topGUI(_aux['parentGUI']))
        top.withdraw()
        top.transient(_aux['parentGUI'])
        top.wm_title('Store shot bookmark with description')
        oldParent = _aux['parentGUI']
        _aux['parentGUI'] = top

        OMFIT['shotBookmarks'].load()

        try:
            OMFIT['scratch']['bookmarksDescription'] = OMFIT['shotBookmarks'][device][str(shot)][str(time)]
        except Exception:
            description = ''

        e = Entry("OMFIT['scratch']['bookmarksDescription']", "Shot description", postcommand=onEscape, default='')
        e.configure(width=30)
        _aux['parentGUI'] = oldParent
        top.bind('<Escape>', lambda event: onEscape())
        top.deiconify()
        top.wait_window(top)

        addBookmarks(device, shot, time, description=OMFIT['scratch']['bookmarksDescription'])
        del OMFIT['scratch']['bookmarksDescription']
        OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

    def linkUnlinkSettings(linked):
        if linked == 'linked':
            printi(rootName + "['SETTINGS']['EXPERIMENT'] is now set only for this module")
            for item in ['device', 'shot', 'time', 'shots', 'times', 'runid']:
                root['SETTINGS']['EXPERIMENT'][item] = evalExpr(root['SETTINGS']['EXPERIMENT'][item])
        else:
            printi(rootName + "['SETTINGS']['EXPERIMENT'] inherits from the parent module or MainSettings")
            for item in ['device', 'shot', 'time', 'shots', 'times', 'runid']:
                root['SETTINGS']['EXPERIMENT'][item] = OMFITexpression(
                    """try:
    return_variable=OMFITmodules[-2]['SETTINGS']['EXPERIMENT']['%s']
except Exception:
    return_variable=MainSettings['EXPERIMENT']['%s']
"""
                    % (item, item)
                )
        OMFITaux['rootGUI'].event_generate("<<update_GUI>>")
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")

    frm1 = ttk.Frame(frm)
    frm1.pack(side=tk.LEFT, expand=tk.NO, fill=tk.BOTH)

    im = tk.PhotoImage(master=frm1, file=os.path.join(OMFITsrc, 'extras', 'graphics', linked + '.ppm'))
    b = ttk.Button(master=frm1, text=linked, image=im, command=lambda linked=linked: linkUnlinkSettings(linked), takefocus=False)
    b._ntimage = im
    b.pack(
        side=[tk.LEFT, tk.TOP][
            int(
                np.sum(
                    [np.iterable(showShot) or showShot, np.iterable(showTime) or showTime, np.iterable(showDevice) or showDevice, showRunID]
                )
                > 2
            )
        ],
        expand=tk.NO,
        fill=tk.NONE,
    )

    im = tk.PhotoImage(master=frm1, file=os.path.join(OMFITsrc, 'extras', 'graphics', 'bookmark.ppm'))
    b = ttk.Button(
        master=frm1,
        text='bookmark',
        image=im,
        command=lambda device=exp['device'], shot=exp['shot'], time=exp['time']: addBookmarksWithDescription(
            exp['device'], exp['shot'], exp['time']
        ),
        takefocus=False,
    )
    b._ntimage = im
    b.pack(
        side=[tk.LEFT, tk.TOP][
            int(
                np.sum(
                    [np.iterable(showShot) or showShot, np.iterable(showTime) or showTime, np.iterable(showDevice) or showDevice, showRunID]
                )
                > 2
            )
        ],
        expand=tk.NO,
        fill=tk.NONE,
    )

    _aux['parentGUI'] = oldParent

    if stopIfNotSet:
        if np.any([not len(list([_f for _f in tolist(k) if evalExpr(_f) is not None])) for k in list(set_values.values())]):
            Label("Device, shot(s) and time(s) entries can not be None!", foreground='red')
            End()

    # set data to be harvested
    set_values['module'] = module['SETTINGS']['MODULE']['ID']
    _aux['harvest'].setdefault(moduleName, {})
    _aux['harvest'][moduleName] = set_values


@_available_to_userGUI
def CloseGUI():
    """
    Function for closing the active user GUI
    """
    _clearClosedGUI(_aux['topGUI'])
    raise EndOMFITpython()


@_available_to_userTASK
def End(what='single'):
    '''
    End execution of OMFITpython script

    :param what:
          * 'single' terminates the running script
          * 'all' terminates the whole workflow
    '''
    if _aux['topGUI'] is not None and not len(OMFITaux['prun_process']):
        _aux['topGUI'].update_idletasks()
    if str(what).lower() == 'all':
        raise EndAllOMFITpython()
    else:
        raise EndOMFITpython()


@_available_to_userGUI
def Open(object):
    '''
    Open OMFITascii object in editor or OMFITweb in browser
    File extension behaviour can be specified in OMFIT['MainSettings']['SETUP']['EXTENSIONS']

    :param object: OMFIT object or filename to be opened in external editor
    '''
    OMFITaux['GUI'].openFile(thisObject=object)


@_available_to_userGUI
def Figure(toolbar=True, returnFigure=False, fillX=False, **kw):
    r"""
    Embed a matplotlib figure in an OMFIT GUI

    :param toolbar: [True] show/hide the figure toolbar

    :param returnFigure: [False] function returns figure `f` or axis `f.add_subplot(111)`

    :param fillX: [False] fill X dimension of screen

    :param figsize: (5*2./3., 4*2./3.) figure size

    :param \**kw: keyword arguments passed to pyplot.Figure
    """

    if fillX:
        fillX = X
    else:
        fillX = tk.NONE

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], fill=tk.X, expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP])

    kw.setdefault('figsize', (5 * 2.0 / 3.0, 4 * 2.0 / 3.0))
    f = pyplot.Figure(**kw)

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.backends._backend_tk import NavigationToolbar2Tk as NavigationToolbar2

    canvas = FigureCanvasTkAgg(f, master=frm_top)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=fillX, expand=tk.YES)

    if toolbar:
        toolbar = NavigationToolbar2(canvas, frm_top)
        toolbar.update_idletasks()

    canvas._tkcanvas.pack(side=tk.TOP, fill=fillX, expand=tk.YES)

    OMFITfigure(f)  # Add enhancements like superzoom

    if returnFigure:
        return f
    else:
        return f.add_subplot(111)


@_available_to_userGUI
def Dialog(*args, **kw):
    """
    Display a dialog box and wait for user input

    :param message: the text to be written in the label

    :param answers: list of possible answers

    :param icon: "question", "info", "warning", "error"

    :param title: title of the frame

    :param options: dictionary of True/False options that are displayed as checkbuttons in the dialog

    :param entries: dictionary of string options that are displayed as entries in the dialog

    :return: return the answer chosen by the user (a dictionary if options keyword was passed)
    """
    kw.setdefault('parent', _aux['parentGUI'])
    return dialog(*args, **kw)


def _setupModule(prefGUI, extraSettings=None):
    from utils_widgets import OMFITfont

    root = relativeLocations(_GUIs[str(_aux['topGUI'])].pythonFile)['root']

    if not _aux['is_compoundGUI']:
        root['__scratch__'].setdefault('showSettings', False)
        root['__scratch__'].setdefault('showStorage', False)

        def showTools():
            try:
                bckp_parent = _aux['parentGUI']
                _aux['parentGUI'] = prefGUI
                _clearKids(_aux['parentGUI'])
                frm = ttk.Frame(_aux['parentGUI'])
                frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

                orient = tk.TOP
                if root['__scratch__']['showStorage'] or root['__scratch__']['showSettings']:
                    orient = tk.LEFT

                def showSettings():
                    root['__scratch__']['showStorage'] = False
                    root['__scratch__']['showSettings'] = not root['__scratch__']['showSettings']
                    showTools()

                frm1 = ttk.Frame(frm)
                frm1.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

                im = tk.PhotoImage(master=frm1, file=os.path.join(OMFITsrc, 'extras', 'graphics', 'settings.ppm'))
                b = ttk.Button(master=frm1, text='settings', image=im, command=showSettings, takefocus=False)
                b._ntimage = im
                b.pack(side=orient, expand=tk.NO, fill=tk.NONE)

                def showStorage():
                    root['__scratch__']['showSettings'] = False
                    root['__scratch__']['showStorage'] = not root['__scratch__']['showStorage']
                    showTools()

                im = tk.PhotoImage(master=frm1, file=os.path.join(OMFITsrc, 'extras', 'graphics', 'storage.ppm'))
                b = ttk.Button(master=frm1, text='storage', image=im, command=showStorage, takefocus=False)
                b._ntimage = im
                b.pack(side=orient, expand=tk.NO, fill=tk.NONE)

                if root['__scratch__']['showStorage'] or root['__scratch__']['showSettings']:
                    ttk.Separator(frm).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=2)

                if root['__scratch__']['showSettings']:
                    Label('SETTINGS: ' + treeLocation(root)[-1], font=OMFITfont('bold', -2))
                    ComboBox(
                        "root['SETTINGS']['REMOTE_SETUP']['serverPicker']", list(SERVER.listServers().keys()), 'server', updateGUI=True
                    )
                    try:
                        location = "OMFIT['MainSettings']['SERVER']['%s']" % SERVER(root['SETTINGS']['REMOTE_SETUP']['serverPicker'])
                    except Exception:
                        Label('Invalid server %s' % str(root['SETTINGS']['REMOTE_SETUP']['serverPicker']))
                    for item in list(eval(location).keys()):
                        Entry(location + "[" + repr(item) + "]", item[0].upper() + item[1:], updateGUI=True)

                    if extraSettings:
                        Separator()
                        extraSettings()

                if root['__scratch__']['showStorage']:
                    Label('STORAGE: ' + treeLocation(root)[-1], font=OMFITfont('bold', -2))

                    def next_runid():
                        # find the run_id with the maximum number
                        index0 = 0
                        for k in root['__STORAGE__'].keys(filter=hide_ptrn):
                            index = int(re.findall('[0-9]+$', k)[-1])
                            if index > index0:
                                root['SETTINGS']['EXPERIMENT']['runid'] = k
                        # go to the next available runid
                        while root['SETTINGS']['EXPERIMENT']['runid'] in root['__STORAGE__'].keys(filter=hide_ptrn):
                            index = re.findall('[0-9]+$', root['SETTINGS']['EXPERIMENT']['runid'])
                            if len(index):
                                root['SETTINGS']['EXPERIMENT']['runid'] = re.sub(
                                    index[-1] + '$', str(int(index[-1]) + 1), root['SETTINGS']['EXPERIMENT']['runid']
                                )
                            else:
                                root['SETTINGS']['EXPERIMENT']['runid'] += '1'
                        root['SETTINGS']['EXPERIMENT']['comment'] = ''

                    def reload_comment(location=None):
                        if root['SETTINGS']['EXPERIMENT']['runid'] in root['__STORAGE__'].keys(filter=hide_ptrn):
                            root['SETTINGS']['EXPERIMENT']['comment'] = root['__STORAGE__'][root['SETTINGS']['EXPERIMENT']['runid']][
                                'comment'
                            ]

                    # handle runids
                    if 'runid' not in root['SETTINGS']['EXPERIMENT'] or root['SETTINGS']['EXPERIMENT']['runid'] == None:
                        root['SETTINGS']['EXPERIMENT']['runid'] = 'sim1'
                    if '__STORAGE__' in root and root['SETTINGS']['EXPERIMENT']['runid'] in root['__STORAGE__'].keys(filter=hide_ptrn):
                        Button('New run-ID', next_runid, updateGUI=True)
                    runs = SortedDict()
                    if '__STORAGE__' in root:
                        for k in root['__STORAGE__'].keys(filter=hide_ptrn):
                            if 'comment' in root['__STORAGE__'][k]:
                                runs[k + ': ' + root['__STORAGE__'][k]['comment']] = k
                    ComboBox(
                        "root['SETTINGS']['EXPERIMENT']['runid']",
                        runs,
                        'Run-ID',
                        state='readonly',
                        check=is_string,
                        default='',
                        updateGUI=True,
                        postcommand=reload_comment,
                    )

                    Separator()
                    Separator()

                    # handle operations
                    state = 'normal'
                    if 'comment' not in root['SETTINGS']['EXPERIMENT'] or not root['SETTINGS']['EXPERIMENT']['comment']:
                        state = 'disabled'
                    Entry("root['SETTINGS']['EXPERIMENT']['comment']", 'Comment', check=is_string, default='', updateGUI=True)
                    if '__STORAGE__' not in root or root['SETTINGS']['EXPERIMENT']['runid'] not in root['__STORAGE__'].keys(
                        filter=hide_ptrn
                    ):
                        Button('Store %s (new)' % root['SETTINGS']['EXPERIMENT']['runid'], root.store, state=state, updateGUI=True)
                    else:
                        Button('Store %s (update)' % root['SETTINGS']['EXPERIMENT']['runid'], root.store, state=state, updateGUI=True)
                        Separator()
                        CheckButton("root['__STORAGE__']['__restoreScripts__']", 'Restore scripts', default=False)
                        Button('Restore %s' % root['SETTINGS']['EXPERIMENT']['runid'], root.restore, updateGUI=True)
                        Separator()
                        Button('Delete %s' % root['SETTINGS']['EXPERIMENT']['runid'], root.destore, updateGUI=True)

            except Exception:
                raise
            finally:
                _aux['parentGUI'] = bckp_parent
                OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")

        showTools()


def clc(tag=None):
    '''
    clear console (possible tags are)
        INFO        : forest green
        HIST        : dark slate gray
        WARNING     : DarkOrange2
        HELP        : PaleGreen4
        STDERR      : red3
        STDOUT      : black
        DEBUG       : gold4
        PROGRAM_OUT : blue
        PROGRAM_ERR : purple

    :param tag: specific tag to clear
    '''
    if OMFITaux['console'] is None:
        return

    from omfit_classes.utils_base import _Streams

    if not tag:
        OMFITaux['console'].clear()

    elif tag.upper() in _Streams.tags:
        OMFITaux['console'].clear(tag)
        if tag == 'STDERR':
            for k in range(10):
                OMFITaux['console'].clear('STDERR' + str(k))

    else:
        printe('clc: console tag `%s` is not recognized. Valid options are:' % tag)
        for tag in _Streams.tags:
            printe('     %s: %s' % (tag.ljust(12), _Streams.tags[tag]))


@_available_to_userGUI
def EditASCIIobject(location, lbl=None, comment=None, updateGUI=False, help='', postcommand=None, url='', **kw):
    """
    This method creates a GUI element that edits ASCII files in the OMFIT tree
    Sample usage::

        OMFITx.EditASCIIobject("root['INPUTS']['TRANSP']", 'edit namelist', postcommand=lambda location:eval(location).load())

    :param location: location of the ASCII OMFITobject in the OMFIT tree (notice that this is a string)

    :param lbl: Label which is put on the left of the entry

    :param comment: A comment which appears on top of the entry

    :param updateGUI: Force a re-evaluation of the GUI script when this parameter is changed

    :param help: help provided when user right-clicks on GUI element (adds GUI button)

    :param postcommand: command to be executed after the value in the tree is updated. This command will receive the OMFIT location string as an input

    :param url: open url in web-browser (adds GUI button)

    :return: associated ttk.Button object
    """
    location = _absLocation(location)
    postcommand_location = reveal_location = location
    scratchLocation = _absLocation("scratch['%s']" % ('editASCII_' + omfit_hash(location, 10)))

    try:
        filename = eval(postcommand_location).filename
    except Exception:
        filename = ''

    frm_top = ttk.Frame(_aux['parentGUI'])
    frm_top.pack(side=_aux['packing'], expand=[tk.YES, tk.NO][_aux['packing'] == tk.TOP], fill=tk.X, padx=5, pady=1)
    if comment is not None:
        frm = ttk.Frame(frm_top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        _Label(frm, comment).pack(side=tk.LEFT)

    frm = ttk.Frame(frm_top)
    frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    if lbl is None:
        lbl = 'Edit ' + location

    def onDone(location):
        with open(filename, 'w') as f:
            f.write(eval(scratchLocation))
        del eval(buildLocation(parseLocation(scratchLocation)[:-1]))[parseLocation(scratchLocation)[-1]]
        if postcommand is not None:
            postcommand(postcommand_location)

    def showText():
        with open(filename, 'r') as f:
            eval(buildLocation(parseLocation(scratchLocation)[:-1]))[parseLocation(scratchLocation)[-1]] = f.read()
        _Text(
            parent=frm,
            location=scratchLocation,
            lbl=lbl,
            updateGUI=updateGUI,
            help=help,
            preentry=None,
            postcommand=onDone,
            percolator=filename.endswith('.py'),
            reveal_location=reveal_location,
            **kw,
        )

    bttn = ttk.Button(frm, text=lbl, command=showText, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X, padx=5, pady=1)
    if len(filename) == 0:
        bttn.state(['disabled'])
    return bttn


# ---------------------------
# file browsing
# ---------------------------
class FileDialog(object):
    """
    Standard remote file selection dialog -- no checks on selected file.

    :param directory: directory where to start browsing

    :param serverPicker: serverPicker wins over server/tunnel settings
                         serverpicker=None will reuse latest server/tunnel that the user browsed to

    :param server: server

    :param tunnel: tunnel

    :param pattern: glob regular expression for files selection

    :param default: default filename selection

    :param master: Tkinter master GUI

    :param lockServer: allow users to change server settings

    :param focus: what to focus in the GUI ('filterDirs','filterFiles')

    :param favorite_list_location: OMFIT tree location which contains a possibly empty list of favorite file directories. To keep with the general omfit approach this should be a string.

    :param pattern_list_location: OMFIT tree location which contains a possibly empty list of favorite search patterns. To keep with the general omfit approach this should be a string.

    :param is_dir: (bool) Whether the requested file is a directory
    """

    def __init__(
        self,
        directory=None,
        serverPicker='',
        server='localhost',
        tunnel='',
        pattern='*',
        default='',
        master=None,
        lockServer=False,
        focus='filterDirs',
        favorite_list_location=None,
        pattern_list_location=None,
        is_dir=False,
        title='File Browser',
    ):

        if master is None:
            master = OMFITaux['rootGUI']
        self.master = master

        self.is_dir = is_dir

        if serverPicker is None:
            printd(server, tunnel, topic='FilePicker')
            if server == 'localhost':
                server = OMFITaux['lastBrowsed'].setdefault('__lastServer__', server)
            if tunnel == '':
                tunnel = OMFITaux['lastBrowsed'].setdefault('__lastTunnel__', tunnel)

        if serverPicker:
            server = SERVER[serverPicker]['server']
            tunnel = SERVER[serverPicker]['tunnel']

        printd(server, tunnel, topic='FilePicker')
        if not server:
            serverPicker = 'localhost'
            server = 'localhost'
            tunnel = ''

        self.favorite_list = None
        if favorite_list_location is not None:
            # This should work correctly - the self.favorite_list is
            # set to the variable in the tree and as a result any updates
            # to this are reflected in the tree entry since lists are
            # modified in place.
            # print("favorite_list_location:",favorite_list_location)
            favorite_list_location = _absLocation(favorite_list_location)
            try:
                self.favorite_list = eval(favorite_list_location)
            except Exception as _excp:
                printe(_excp)
                # if there is a problem with evaluation turn off the option
                print("favorite_list_Location could not be evaluated: %s" % favorite_list_location)
                favorite_list_location = None
            else:
                # if a list is not passed in then turn this off
                if not isinstance(self.favorite_list, list):
                    self.favorite_list = None
                    favorite_list_location = None

        self.pattern_list = None
        if pattern_list_location is not None:
            # This should work correctly - the self.favorite_list is
            # set to the variable in the tree and as a result any updates
            # to this are reflected in the tree entry since lists are
            # modified in place.
            # print("pattern_list_location:",pattern_list_location)
            pattern_list_location = _absLocation(pattern_list_location)
            try:
                self.pattern_list = eval(pattern_list_location)
            except Exception as _excp:
                printe(_excp)
                # if there is a problem with evaluation turn off the option
                print("pattern_list_Location could not be evaluated: %s" % pattern_list_location)
                pattern_list_location = None
            else:
                # if a list is not passed in then turn this off
                if not isinstance(self.pattern_list, list):
                    self.pattern_list = None
                    pattern_list_location = None

        self.server0, self.tunnel0 = server, tunnel
        printd(self.server0, self.tunnel0, topic='FilePicker')

        self.pattern = pattern
        self.default = default

        # set the top level window
        self.top = tk.Toplevel(master)
        self.top.withdraw()
        self.top.transient(master)
        self.title = title

        def tab_complete():
            def complete(what, options):
                options = list(map(os.path.abspath, options))
                what = os.path.abspath(what)
                possible_options = [item + os.sep for item in options if item.startswith(what)]
                return os.path.commonprefix(possible_options), possible_options

            filter_get = self.get_filter()[0]
            selection_get = self.selection.get()
            if os.path.abspath(os.path.split(filter_get)[0]) != os.path.abspath(selection_get) and os.path.abspath(
                filter_get
            ) != os.path.abspath(selection_get):
                self.filter_command(dir=os.path.abspath(os.path.split(filter_get)[0]))
            completed = complete(filter_get, [os.path.split(filter_get)[0] + os.sep + item for item in self.dirs.get(0, tk.END)])
            if completed[0]:
                self.filterDirs.delete(0, tk.END)
                self.filterDirs.insert(tk.END, re.sub('//', '/', completed[0]))
                if len(completed[1]) == 1 and completed[0].endswith('/'):
                    self.filter_command()
            self.filterDirs.xview(tk.END)
            return 'break'

        def fill_server_tunnel():
            tmp = self.comboBox.get().split(' -- ')[0]
            serverTK.set(str(SERVER[tmp]['server']))
            tunnelTK.set(str(SERVER[tmp].get('tunnel', '')))
            set_server_tunnel()

        def set_server_tunnel():
            serverTK.set(serverTK.get().strip())
            try:
                serverTK.set(SERVER[serverTK.get().strip()]['server'])
                tunnelTK.set(SERVER[serverTK.get().strip()]['tunnel'])
            except Exception:
                tunnelTK.set(tunnelTK.get().strip())
            self.server0 = serverTK.get()
            self.tunnel0 = tunnelTK.get()
            self.go(directory=None)

        # Set server string
        serverTK = tk.StringVar()
        serverTK.set(self.server0)

        # Set tunnel string
        tunnelTK = tk.StringVar()
        tunnelTK.set(self.tunnel0)

        # set frame from top level window
        frm = ttk.Frame(self.top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

        # add another frame for the server and tunnel information
        frm1 = ttk.Frame(frm)
        ttk.Label(frm1, text='Fill server/tunnel from: ').pack(side=tk.LEFT)
        tmp = list(SERVER.listServers().values())

        # convert everything to lower case - could be a problem if folks use case to distinguish servers
        tmp.sort(key=lambda x: x.lower())
        tmp = [tmp.pop(tmp.index(SERVER.listServers()['localhost']))] + tmp

        # setup a comboBox for choosing the server based on the list in mainSettings - SERVER is a global
        self.comboBox = ttk.Combobox(frm1, state='readonly', values=tmp)
        self.comboBox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.comboBox.bind('<<ComboboxSelected>>', lambda event: fill_server_tunnel())
        frm1.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        # add aonther frame for the server label and entry
        frm1 = ttk.Frame(frm)
        ttk.Label(frm1, text='On server: ').pack(side=tk.LEFT)
        serverTKGUI = ttk.Entry(frm1, textvariable=serverTK)
        serverTKGUI.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        serverTKGUI.bind('<Return>', lambda event: set_server_tunnel())
        frm1.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        # add another frame for the tunnel label and entry
        frm1 = ttk.Frame(frm)
        ttk.Label(frm1, text='Via tunnel: ').pack(side=tk.LEFT)
        tunnelTKGUI = ttk.Entry(frm1, textvariable=tunnelTK)
        tunnelTKGUI.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        tunnelTKGUI.bind('<Return>', lambda event: set_server_tunnel())
        frm1.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        # if server is locked then turn off selection functionality
        if lockServer:
            self.comboBox.configure(state='disabled')
            serverTKGUI.configure(state='disabled')
            tunnelTKGUI.configure(state='disabled')

        # add a separator to the main frame
        ttk.Separator(frm).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=2)

        # add the bottom frame showing the file selection - why is this here?
        self.botframe = ttk.Frame(self.top)
        self.botframe.pack(side=tk.BOTTOM, fill=tk.X)

        # Add another frame to the main window
        frm = ttk.Frame(self.top)
        ttk.Separator(frm).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=5, pady=2)
        frm.pack(side=tk.BOTTOM, fill=tk.X)
        # add label and entry to show file selection at the bottom
        ttk.Label(frm, text='Selection: ').pack(side=tk.LEFT)
        self.selection = ttk.Entry(frm)
        self.selection.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.selection.bind('<Return>', lambda event: self.ok_command())

        # create a middle frame
        self.midframe = ttk.Frame(self.top)
        self.midframe.pack(expand=tk.YES, fill=tk.BOTH)

        # create a scroll bar in the middle frame to scroll file names
        self.filesbar = ttk.Scrollbar(self.midframe)
        self.filesbar.pack(side=tk.RIGHT, fill=tk.Y)

        # create another frame as part of midframe to hold file filter and files
        frm = ttk.Frame(self.midframe)
        frm.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)

        # branch on whether pattern_list favorites are asked for
        if pattern_list_location is None:

            # add a file filter
            self.filterFiles = ttk.Entry(frm)
            self.filterFiles.pack(side=tk.TOP, fill=tk.X)
            self.filterFiles.bind('<Return>', lambda event: self.filter_command())

            # add the files list box
            self.files = tk.Listbox(frm, exportselection=0, yscrollcommand=(self.filesbar, 'set'))
            self.files.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)

            # not sure what the first lines are doing - the rest bind event handlers
            btags = self.files.bindtags()
            self.files.bindtags(btags[1:] + btags[:1])
            self.files.bind('<ButtonRelease-1>', lambda event: self.files_select_event())
            self.files.bind('<Double-ButtonRelease-1>', lambda event: self.ok_command())
            self.files.bind('<Return>', lambda event: self.ok_command())

            # connect the files scrollbar
            self.filesbar.config(command=(self.files, 'yview'))

        else:  # add extra frames to manage pattern list buttons

            # These are together because both frma and frmb are in frm
            # create frame for file filter and filter list buttons
            # expand is off for frma so it does not expand to file half the space
            frma = ttk.Frame(frm)
            frma.pack(side=tk.TOP, fill=tk.X)
            # create frame for file list
            frmb = ttk.Frame(frm)
            frmb.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

            # setup a comboBox for choosing the file filter pattern from favorites - add to frame a
            self.filterFiles = ttk.Combobox(frma, state='normal', values=self.pattern_list)
            self.filterFiles.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            self.filterFiles.bind('<<ComboboxSelected>>', lambda event: self.filter_command())
            self.filterFiles.bind('<Return>', lambda event: self.filter_command())

            # Add add_to_favorite_patterns button
            self.add_to_favorite_patterns = ttk.Button(
                frma, text="+", command=lambda: self.manage_list(self.pattern_list, self.filterFiles, '+')
            )
            self.add_to_favorite_patterns.pack(side=tk.LEFT)
            # Add remove_from_favorite_patterns button
            self.remove_from_favorite_patterns = ttk.Button(
                frma, text="-", command=lambda: self.manage_list(self.pattern_list, self.filterFiles, '-')
            )
            self.remove_from_favorite_patterns.pack(side=tk.LEFT)

            # add the files list box in frame b
            self.files = tk.Listbox(frmb, exportselection=0, yscrollcommand=(self.filesbar, 'set'))
            self.files.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)

            # not sure what the first lines are doing - the rest bind event handlers
            btags = self.files.bindtags()
            self.files.bindtags(btags[1:] + btags[:1])
            self.files.bind('<ButtonRelease-1>', lambda event: self.files_select_event())
            self.files.bind('<Double-ButtonRelease-1>', lambda event: self.ok_command())
            self.files.bind('<Return>', lambda event: self.ok_command())

            # connect the files scrollbar
            self.filesbar.config(command=(self.files, 'yview'))

        # add directory list scroll bar
        self.dirsbar = ttk.Scrollbar(self.midframe)
        self.dirsbar.pack(side=tk.LEFT, fill=tk.Y)

        # add another frame for the directory information
        frm = ttk.Frame(self.midframe)
        frm.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)

        # branch on whether favorite list is requested for directories
        if favorite_list_location is None:

            # add the directory filter
            self.filterDirs = ttk.Entry(frm)
            self.filterDirs.pack(side=tk.TOP, fill=tk.X)
            self.filterDirs.bind('<Return>', lambda event: self.filter_command())
            self.filterDirs.bind('<Tab>', lambda event: tab_complete())
            self.filterDirs.bind('<Shift-Tab>', lambda event: self.dirs_back_event())
            try:
                self.filterDirs.bind('<ISO_Left_Tab>', lambda event: self.dirs_back_event())
            except tk.TclError:
                pass

            # add the directory list
            self.dirs = tk.Listbox(frm, exportselection=0, yscrollcommand=(self.dirsbar, 'set'))
            self.dirs.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
            # bind events for directory selection
            btags = self.dirs.bindtags()
            self.dirs.bindtags(btags[1:] + btags[:1])
            self.dirs.bind('<ButtonRelease-1>', lambda event: None)
            self.dirs.bind('<Double-ButtonRelease-1>', lambda event: self.dirs_double_event())
            self.dirs.bind('<Return>', lambda event: self.dirs_double_event())
            self.dirs.bind('<BackSpace>', lambda event: self.dirs_back_event())

            # connect the directory scrollbar
            self.dirsbar.config(command=(self.dirs, 'yview'))

        else:  # if there is a favorite list add some frames

            # create frame for directory filter and directory filter buttons
            frma = ttk.Frame(frm)
            frma.pack(side=tk.TOP, fill=tk.X)
            # create frame for list of directories
            frmb = ttk.Frame(frm)
            frmb.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

            # setup a comboBox for choosing the directory filter pattern from favorites - add to frame a
            self.filterDirs = ttk.Combobox(frma, state='normal', values=self.favorite_list)
            self.filterDirs.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            self.filterDirs.bind('<<ComboboxSelected>>', lambda event: self.filter_command())
            self.filterDirs.bind('<Return>', lambda event: self.filter_command())
            self.filterDirs.bind('<Tab>', lambda event: tab_complete())
            self.filterDirs.bind('<Shift-Tab>', lambda event: self.dirs_back_event())
            try:
                self.filterDirs.bind('<ISO_Left_Tab>', lambda event: self.dirs_back_event())
            except tk.TclError:
                pass

            # Add add_to_favorite_dirs button
            self.add_to_favorite_dirs = ttk.Button(
                frma, text="+", command=lambda: self.manage_list(self.favorite_list, self.filterDirs, '+')
            )
            self.add_to_favorite_dirs.pack(side=tk.LEFT)
            # Add remove_from_favorite_dirs button
            self.remove_from_favorite_dirs = ttk.Button(
                frma, text="-", command=lambda: self.manage_list(self.favorite_list, self.filterDirs, '-')
            )
            self.remove_from_favorite_dirs.pack(side=tk.LEFT)

            # add the directory list
            self.dirs = tk.Listbox(frmb, exportselection=0, yscrollcommand=(self.dirsbar, 'set'))
            self.dirs.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
            # bind events for directory selection
            btags = self.dirs.bindtags()
            self.dirs.bindtags(btags[1:] + btags[:1])
            self.dirs.bind('<ButtonRelease-1>', lambda event: None)
            self.dirs.bind('<Double-ButtonRelease-1>', lambda event: self.dirs_double_event())
            self.dirs.bind('<Return>', lambda event: self.dirs_double_event())
            self.dirs.bind('<BackSpace>', lambda event: self.dirs_back_event())
            # connect the directory scrollbar
            self.dirsbar.config(command=(self.dirs, 'yview'))

        # Add ok button to the bottom of the frame
        self.ok_button = ttk.Button(self.botframe, text="Ok", command=self.ok_command)
        self.ok_button.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        # Add the cancel button to the bottom of the frame
        self.cancel_button = ttk.Button(self.botframe, text="Cancel", command=self.quit)
        self.cancel_button.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        self.top.protocol('WM_DELETE_WINDOW', self.quit)
        self.top.bind('<Escape>', lambda event: self.quit())

        tk_center(self.top, self.master, 800, 600)
        self.top.deiconify()
        self.top.update_idletasks()

        self.go(directory)

        if focus == 'filterFiles':
            self.filterFiles.focus_set()
            self.filterFiles.icursor(0)
        elif focus == 'filterDirs':
            self.filterDirs.focus_set()

        self.top.wait_window(self.top)
        self.top.destroy()

    def go(self, directory=None):
        if directory is None:
            if self.server0 + '-' + self.tunnel0 in OMFITaux['lastBrowsed']:
                directory = OMFITaux['lastBrowsed'][self.server0 + '-' + self.tunnel0]
            else:
                directory = ''

        try:
            serverPicker = SERVER(SERVER[self.server0]['server'])
            self.comboBox.set(serverPicker + ' -- ' + self.server0)
        except KeyError:
            pass

        self.curdir = directory
        self.directory = directory
        self.set_filter(self.directory, self.pattern)
        self.set_selection(self.default)
        self.how = None
        self.filter_command()
        self.filterDirs.xview(tk.END)

    def quit(self, how=None):
        if how is None:
            self.how = None
        else:
            self.how = how, self.server0, self.tunnel0
        self.top.destroy()

    def dirs_double_event(self):
        dir, pat = self.get_filter()
        subdir = self.dirs.get('active')
        dir = os.path.normpath(os.path.join(dir, subdir))
        self.set_filter(dir, pat)
        self.filter_command()

    def dirs_back_event(self):
        dir, pat = self.get_filter()
        dir = os.path.normpath(os.path.join(dir, '..'))
        self.set_filter(dir, pat)
        self.filter_command()
        return 'break'

    def files_select_event(self):
        file = self.files.get('active')
        self.set_selection(file)

    def ok_command(self):
        self.quit(self.get_selection())

    def remote_command(self, command):
        self.top.title('%s: %s' % (self.title, parse_server(self.server0)[2]))
        self.username, self.server, self.port = setup_ssh_tunnel(self.server0, self.tunnel0)

        def ssh_cd(inv):
            if is_localhost(self.server0):
                return inv
            return (
                sshOptions()
                + controlmaster(self.username, self.server, self.port, self.server0)
                + " -Y -q -p "
                + self.port
                + " "
                + self.username
                + "@"
                + self.server
                + " '"
                + inv
                + "'"
            )

        child = subprocess.Popen(ssh_cd(command), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = map(b2s, child.communicate())
        if child.poll() == 0:
            pass
        elif child.poll() and len(out.strip()):
            printw('Warning in file browser:\n\n%s' % err)
        elif child.poll():
            raise Exception('Error in file browser:\n\n%s' % err)
        return out, err, child.poll()

    def filter_command(self, dir=None):
        dir0, pat = self.get_filter()
        if dir is None:
            dir = dir0
        strdir = "\"" + dir + "\"" if dir else ''
        try:
            out, err, retcode = self.remote_command("cd {dir} && \\pwd && \\ls -1 -p -L {dir}".format(dir=strdir))
            self.filterDirs.configure(foreground='black')
        except Exception as _excp:
            printe(_excp)
            self.filterDirs.configure(foreground='red')
            return
        names = list([x.strip() for x in out.strip().split('\n')])
        dir = names.pop(0) + os.sep
        self.directory = dir
        self.set_filter(dir, pat)
        OMFITaux['lastBrowsed'][self.server0 + '-' + self.tunnel0] = dir
        OMFITaux['lastBrowsed']['__lastServer__'] = self.server0
        OMFITaux['lastBrowsed']['__lastTunnel__'] = self.tunnel0
        names.sort(key=lambda x: x.lower())
        if self.directory != '/':
            subdirs = [os.pardir]
        else:
            subdirs = []
        if self.is_dir:
            matchingfiles = ['.']
        else:
            matchingfiles = []
        for name in names:
            fullname = os.path.join(dir, name)
            if fullname.endswith('/') or os.path.isdir(fullname):
                subdirs.append(name)
            elif fnmatch.fnmatch(name, pat):
                matchingfiles.append(name)
        self.dirs.delete(0, tk.END)
        for name in subdirs:
            self.dirs.insert(tk.END, name)
        self.files.delete(0, tk.END)
        for name in matchingfiles:
            self.files.insert(tk.END, name)
        head, tail = os.path.split(self.get_selection())
        if tail == self.curdir:
            tail = ''
        self.set_selection(tail)

    def get_filter(self):
        return re.sub('//', '/', self.filterDirs.get()), self.filterFiles.get()

    def get_selection(self):
        selection = self.selection.get().replace('//', '/')
        if self.is_dir:
            if not selection.endswith('/'):
                selection = os.path.dirname(selection) + '/'
        return selection

    def set_filter(self, dir, pat):
        pat = pat.strip()
        if not pat:
            pat = self.get_filter()[-1]
            if not pat:
                pat = "*"
        self.filterDirs.delete(0, tk.END)
        self.filterDirs.insert(tk.END, re.sub('//', '/', dir))
        self.filterFiles.delete(0, tk.END)
        self.filterFiles.insert(tk.END, re.sub('//', '/', pat))

    def set_selection(self, file):
        self.selection.delete(0, tk.END)
        self.selection.insert(tk.END, re.sub('//', '/', os.path.join(self.directory, file)))
        self.selection.xview(tk.END)

    def manage_list(self, fav_list, obj, op):
        # obj is expected to be a combobox object from the FileDialog class (for either filterFiles or filterDirs)
        # get value from combobox object
        value = obj.get()
        if op == '+':
            printd('FileDialog:manage_list:add:', value)
            if value not in fav_list:
                fav_list.append(value)
        elif op == '-':
            printd('FileDialog:manage_list:remove:', value)
            if value in fav_list:
                fav_list.remove(value)

        # update combobox selections
        obj['values'] = fav_list


class LoadFileDialog(FileDialog):
    """File selection dialog which checks that the file exists."""

    def __init__(self, *args, **kw):
        self.transferRemoteFile = kw.pop('transferRemoteFile', False)
        super().__init__(*args, **kw)

    def ok_command(self):
        file = self.get_selection()
        self.remote_command('\\ls "{}"'.format(file))
        # transfer remote file locally if requested
        if self.transferRemoteFile and not is_localhost(self.server0):
            if isinstance(self.transferRemoteFile, str):
                directory = self.transferRemoteFile
            else:
                directory = OMFITcwd + os.sep + 'dir_' + utils_base.now("%Y-%m-%d__%H_%M_%S__%f")
                while os.path.exists(directory):
                    directory += '_'
            if not os.path.exists(directory):
                os.makedirs(directory)
            remote_downsync(self.server0, file, directory + os.sep, self.tunnel0)
            self.server0 = 'localhost'
            self.tunnel0 = ''
            self.quit(directory + os.sep + os.path.split(file)[1])
        else:
            self.quit(file)


class SaveFileDialog(FileDialog):
    """File selection dialog which checks that the file exists before saving."""

    def ok_command(self):
        file = self.get_selection()
        try:
            self.remote_command('\\ls "{}"'.format(file))

            answer = Dialog('Overwrite %s ?' % file, answers=['Yes', 'No'], icon='question', title='File exists', parent=self.top)
        except Exception:
            answer = 'Yes'
        if answer == 'Yes':
            self.quit(file)
        else:
            pass


def remoteFile(
    parent=None,
    transferRemoteFile=True,
    remoteFilename=None,
    server=None,
    tunnel=None,
    init_directory_location=None,
    init_pattern_location=None,
    favorite_list_location=None,
    pattern_list_location=None,
    is_dir=False,
):
    '''
    Opens up a dialogue asking filename, server/tunnel for remote file transfer
    This function is mostly used within the framework; for use in OMFIT GUI scripts
    please consider using the OMFITx.FilePicker and OMFITx.ObjectPicker functions instead.

    :param parent: Tkinter parent GUI

    :param transferRemoteFile: [True,False,None] if True the remote file is transferred to the OMFITcwd directory

    :param remoteFilename: initial string for remote filename

    :param server: initial string for server

    :param tunnel: initial string for tunnel

    :param init_directory_location: The contents of this location are used to set the initial directory for file searches.
                                    If a file name is specified the directory will be determined from the file name and this input ignored.
                                    Otherwise, if set this will be used to set the initial directory.

    :param init_pattern_location: The default pattern is '*'. If this is specified then the contents of the tree location will replace the default intial pattern.

    :param favorite_list_location: OMFIT tree location which contains a possibly empty list of favorite file directories. To keep with the general omfit approach this should be a string.

    :param pattern_list_location: OMFIT tree location which contains a possibly empty list of favorite search patterns. To keep with the general omfit approach this should be a string.

    :return: is controlled with transferRemoteFile parameter

        * string with local filename (if transferRemoteFile==True)

        * string with the filename (if transferRemoteFile==False)

        * tuple with the filename,server,tunnel (if transferRemoteFile==None)
    '''

    # if server is specified do not reuse last server
    serverPicker = None
    if server is not None:
        serverPicker = ''

    default = ''
    directory = None
    if remoteFilename is not None:
        if server is not None:
            directory, default = os.path.split(remoteFilename)
        else:
            default = os.path.split(remoteFilename)[1]
            directory = None

    # allow specification of initial directory
    if directory is None and init_directory_location is not None:
        # if the initial directory is a non-empty string then assign the
        # value to the starting directory
        init_directory_loc = _absLocation(init_directory_location)
        try:
            init_directory = eval(init_directory_loc)
            if init_directory != '' and isinstance(init_directory, str):
                directory = init_directory
        except Exception:
            pass

    # allow specification of initial pattern
    if init_pattern_location is not None:
        # if there is any issue with the evaluation set the search pattern to the default
        init_pattern_loc = _absLocation(init_pattern_location)
        try:
            pattern = eval(init_pattern_loc)
        except Exception:
            print("RemoteFile: Problem evaluating the contents of %s" % init_pattern_loc)
            pattern = '*'
    else:
        pattern = '*'

    if transferRemoteFile:
        fd = LoadFileDialog(
            directory=directory,
            serverPicker=serverPicker,
            server=server,
            tunnel=tunnel,
            pattern=pattern,
            master=parent,
            default=default,
            transferRemoteFile=transferRemoteFile,
            favorite_list_location=favorite_list_location,
            pattern_list_location=pattern_list_location,
            is_dir=is_dir,
        )
    else:
        fd = FileDialog(
            directory=directory,
            serverPicker=None,
            server=server,
            tunnel=tunnel,
            pattern=pattern,
            master=parent,
            default=default,
            favorite_list_location=favorite_list_location,
            pattern_list_location=pattern_list_location,
            is_dir=is_dir,
        )

    if fd.how is None:
        return

    # return either the filename, or a tuple with filename,sever,tunnel if transferRemoteFile is None
    if transferRemoteFile is None:
        return fd.how[0], fd.how[1], fd.how[2]
    else:
        return fd.how[0]


# ---------------------------
# tool functions
# ---------------------------
@_available_to_userTASK
def remote_sysinfo(server, tunnel='', quiet=False):
    r'''
    This function retrieves information from a remote server (like the shell which is running there)::

        {'ARG_MAX': 4611686018427387903,
         'QSTAT': '',
         'SQUEUE': '/opt/slurm/default/bin/squeue',
         'environment': OMFITenv([]),
         'id': 6216321643098941518,
         'login': ['.cshrc', '.login'],
         'logout': ['.logout'],
         'shell': 'csh',
         'shell_path': '/bin/csh',
         'sysinfo': 'csh\nARG_MAX=4611686018427387903\nQSTAT=\nSQUEUE=/opt/slurm/default/bin/squeue\necho: No match.'
        }

    Information from the remote server is stored in a dictionary

    :param server: remote server

    :param tunnel: via tunnel

    :param quiet: suppress output or not

    :return: dictionary with info from the server
    '''
    server0 = server
    tunnel0 = tunnel

    username, server, port = setup_ssh_tunnel(server0, tunnel0)

    def ssh_cd(inv):
        if is_localhost(server0):
            return inv
        return (
            sshOptions()
            + controlmaster(username, server, port, server0)
            + " -t -t -Y -q -p "
            + port
            + " "
            + username
            + "@"
            + server
            + " '"
            + inv
            + "'"
        )

    id_ = omfit_hash(str(username + server + port))
    if id_ in OMFITaux['sysinfo'] and len(
        set(['id', 'sysinfo', 'shell', 'login', 'logout']).difference(set(OMFITaux['sysinfo'][id_].keys()))
    ):
        del OMFITaux['sysinfo'][id_]
    if id_ not in OMFITaux['sysinfo']:
        command = ''
        if 'iter.org' in server0:
            command = '''
touch ~/.nomotdnx
touch ~/.nomotd
'''.lstrip()
        command += '''
echo '-----------OMFIT-----------'
echo SHELL=$0
echo SHELL_PATH=`which $0`
echo ARG_MAX=`getconf ARG_MAX`
echo QSTAT=`which qstat | grep -v "not found"`
echo SQUEUE=`which squeue | grep -v "not found"`
echo '------------ENV------------'
env
echo '------------ENV------------'
'''.strip()
        if not quiet:
            printi(command)
        command = re.sub('\n', ' ; ', command)
        std_out = []
        if not quiet:
            printi('Collecting remote system info')

        _system(ssh_cd(command), message='Collecting remote system info', ignoreReturnCode=True, std_out=std_out, quiet=quiet)

        std_out = [_f for _f in std_out if _f]
        if not len(std_out):
            raise Exception(
                (
                    'Could not reach {username}@{server}:{port}\n\n'
                    '   Possible causes:\n'
                    '1. Do you have an account on `{server}` ?\n'
                    '   -> request an account\n'
                    '2. Is `{username}` your username on `{server}`?\n'
                    "   -> edit your username under OMFIT['MainSettings']['SERVER']\n"
                    '3. Do you have your SSH keys setup on `{server}`?\n'
                    '   -> run `omfit -s` to setup password-less access\n'
                ).format(username=username, server=server, port=port)
            )

        OMFITaux['sysinfo'][id_] = {}
        OMFITaux['sysinfo'][id_]['id'] = id_
        OMFITaux['sysinfo'][id_]['sysinfo'] = '\n'.join(std_out)
        env = False
        ENV = []
        for k in range(len(std_out)):
            if env is None:
                if std_out[k].startswith('SHELL='):
                    OMFITaux['sysinfo'][id_]['shell'] = std_out[k].split('=')[1].strip().split('/')[-1]
                elif std_out[k].startswith('SHELL_PATH='):
                    OMFITaux['sysinfo'][id_]['shell_path'] = std_out[k].split('=')[1].strip()
                elif std_out[k].startswith('ARG_MAX='):
                    OMFITaux['sysinfo'][id_]['ARG_MAX'] = int(std_out[k].split('=')[1].strip())
                elif std_out[k].startswith('QSTAT='):
                    OMFITaux['sysinfo'][id_]['QSTAT'] = std_out[k].split('=')[1].strip()
                elif std_out[k].startswith('SQUEUE='):
                    OMFITaux['sysinfo'][id_]['SQUEUE'] = std_out[k].split('=')[1].strip()
            if '-----------OMFIT-----------' in std_out[k]:
                env = None
            elif '------------ENV------------' in std_out[k]:
                env = not env
            elif env is True:
                ENV.append(std_out[k])

        if not quiet:
            printi(OMFITaux['sysinfo'][id_]['shell'].upper() + ' shell detected: ' + OMFITaux['sysinfo'][id_]['shell_path'])

        if 'shell' not in OMFITaux['sysinfo'][id_]:
            OMFITaux['sysinfo'][id_]['shell'] = ''
        # overview on http://kb.iu.edu/data/abdy.html
        if OMFITaux['sysinfo'][id_]['shell'] == 'tcsh':
            # from http://www.bo.infn.it/alice/alice-doc/mll-doc/impgde/node23.html
            login = ['/etc/csh.cshrc', '/etc/csh.login', '$HOME/.cshrc', '$HOME/.tcshrc', '$HOME/.login']
            logout = ['/etc/csh.logout', '$HOME/.logout']
        elif OMFITaux['sysinfo'][id_]['shell'] == 'csh':
            login = ['.cshrc', '.login']
            logout = ['.logout']
        elif OMFITaux['sysinfo'][id_]['shell'] in ['sh', 'ksh']:
            # https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html
            login = ['/etc/profile', '/etc/ksh.kshrc', '$HOME/.profile']
            logout = []
        elif OMFITaux['sysinfo'][id_]['shell'] == 'bash':
            # https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html
            # from http://shreevatsa.wordpress.com/2008/03/30/zshbash-startup-files-loading-order-bashrc-zshrc-etc/
            # echo exit | strace bash -li |& less | grep '^open'
            login = [
                '/etc/profile',
                '/etc/bash.bashrc',
                '/etc/bashrc',
                '$HOME/.bashrc',
                '$HOME/.bash_profile',
                '$HOME/.bash_login',
                '$HOME/.profile',
            ]
            logout = ['$HOME/.bash_logout', '/etc/bash.bash_logout']
        elif OMFITaux['sysinfo'][id_]['shell'] == 'zsh':
            # https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html
            # from http://shreevatsa.wordpress.com/2008/03/30/zshbash-startup-files-loading-order-bashrc-zshrc-etc/
            login = [
                '/etc/zshenv',
                '$HOME/.zshenv',
                '/etc/zprofile',
                '$HOME/.zprofile',
                '/etc/zshrc',
                '$HOME/.zshrc',
                '/etc/zlogin',
                '$HOME/.zlogin',
            ]
            logout = ['$HOME/.zlogout', '/etc/zlogout']
        elif OMFITaux['sysinfo'][id_]['shell'] == 'rc':
            login = ['.rcrc']
            logout = []
        else:
            login_ok = login = []
            logout = []

        if len(login):
            # find what login files are there
            std_out = []
            std_err = []
            _system(
                ssh_cd('\\ls -1 ' + ' '.join(login)),
                message='Collecting remote system info',
                ignoreReturnCode=True,
                std_out=std_out,
                std_err=std_err,
                quiet=quiet,
            )
            login_ok = []
            for line in std_out + std_err:
                line = line.strip()
                if (
                    len(line)
                    and 'cannot' not in line.lower()
                    and 'no such file or directory' not in line.lower()
                    and ': ' not in line.lower()
                ):
                    login_ok.append(line)
            if not quiet:
                printi('Source files at login: ' + ' '.join(login_ok))

        OMFITaux['sysinfo'][id_]['login'] = login_ok
        OMFITaux['sysinfo'][id_]['logout'] = logout
        OMFITaux['sysinfo'][id_]['environment'] = OMFITenv(string='\n'.join(ENV))

        # expand environmental variables defined in the environment on the server side
        try:
            serverPicker = SERVER(server0)
        except (TypeError, NameError):  # If running outside the framework
            pass
        else:
            if (
                serverPicker in list(SERVER.keys())
                and 'workDir' in SERVER[serverPicker]
                and isinstance(SERVER[serverPicker]['workDir'], str)
                and '$' in SERVER[serverPicker]['workDir']
            ):
                tmp = evalExpr(SERVER[serverPicker]['workDir'])
                for item in re.findall(r'\$\w+', tmp):
                    tmp = tmp.replace(item, OMFITaux['sysinfo'][id_]['environment'][item.strip('$')])
                OMFIT['MainSettings']['SERVER'][serverPicker]['workDir'] = tmp
                OMFIT.addMainSettings(updateUserSettings=True)
                raise OMFITexception('User configuration for `%s` server has been initialized. Try again.' % serverPicker)

    return OMFITaux['sysinfo'][id_]


def manage_user_errors(command, reportUsersErrorByEmail=False, **kw):
    """
    This method wraps around users calls of _OMFITpython scripts and manages printout of errors

    :param command: command to be executed

    :return: whatever the command returned
    """
    if not callable(command):
        raise ValueError('manage_user_errors `command` should be a callable function')

    try:
        tmp = command(**kw)
        return tmp, False

    except (EndOMFITpython, EndAllOMFITpython):
        return None, False

    except Exception as handled_exception:
        etype, value, tb = sys.exc_info()
        excpStack = traceback.format_exception(etype, value, tb)

        # record the full exception stack
        OMFITaux['lastUserError'] = excpStack

        # find out what is the last user error
        kuser = None
        showExcp = False
        inconsole = False
        for k in range(len(excpStack)):
            if 'GlobLoc' in excpStack[k]:
                showExcp = True
            elif showExcp:
                if OMFITcwd in excpStack[k] or re.match(r'  File "OMFIT.*", line [0-9]*.*', excpStack[k]):
                    kuser = k
                    if '____console____.py' in excpStack[k]:
                        inconsole = True
        # if kuser is not found report the whole error
        if kuser is None:
            raise

        # print and highlight the latest user error
        moduleExceptionText = ''
        if inconsole:
            printe("\nException in command box script:")
        else:
            try:
                if OMFITaux['lastRunModule'] != 'OMFIT':
                    eval(OMFITaux['lastRunModule'])
                    printe("\nException in script of module %s:" % str(OMFITaux['lastRunModule']))
                    moduleExceptionText = ' [' + str(eval(OMFITaux['lastRunModule']).ID) + ']'
            except Exception:
                printe("\nException in script:")
        showExcp = False

        # simplify exception by hiding the top part of the stack
        simpleExcp = ''
        for k, line in enumerate(excpStack):
            if 'GlobLoc' in line:
                showExcp = True
            elif showExcp:
                if re.match(r'  File ".*____console____.py", line [0-9]*.*', line):
                    linenumber = re.findall(r'.*line ([0-9]+)*', line)[0]
                    line = 'Error in command box' + '\n' + line.split('\n')[1]
                elif os.path.abspath(OMFITcwd) in line:
                    filename = re.findall(r'  File "(.*)"', line)
                    if len(filename):
                        filename = os.path.split(filename[0])[1]
                    else:
                        filename = line
                    linenumber = re.findall(r'.*line ([0-9]+)*', line)
                    if len(linenumber):
                        linenumber = '" at line  ' + linenumber[0] + '\n'
                    else:
                        linenumber = ''
                    line = 'Error in "' + filename + linenumber + line.split('\n')[1]
                elif re.match(r'  File "', line):
                    continue
                simpleExcp += line + '\n'
        if isinstance(handled_exception, OMFITexception):
            simpleExcp = repr(handled_exception)
        simpleExcp += '\nPress <F6> to see full error report...\n'

        # list of developers
        developers = tolist(OMFIT['MainSettings']['SETUP']['report_to'], empty_lists=[None, ''])
        try:
            if OMFITaux['lastRunModule'] != 'OMFIT':
                developers += eval(OMFITaux['lastRunModule']).contact
        except Exception as _excp1:
            printe(_excp1)
        developers = list(set(developers))

        # check if this error is the same as the last error that was reported
        lastSeen = False
        if '\n'.join(OMFITaux.setdefault('lastReportedUserError', [''])) == '\n'.join(excpStack):
            lastSeen = True

        # files attachments (relevant python scripts, MainSettings, and module settings)
        files = []
        lines = re.findall(r'  File ".*", line [0-9]+.*', '\n'.join(excpStack))
        for line in lines:
            filename = re.sub(r'  File "(.*)", line [0-9]+.*', r'\1', line)
            if OMFITcwd in filename:
                files.append(filename)
        files = unsorted_unique(files[::-1])[::-1]

        creator = ['']
        if files:
            # see who created the python file by parsing the header '# Created by ...'
            with open(files[-1], 'r') as f:
                creator = re.findall(r'\#\s+\w+\s+by\s+\w+\s*.*', '/n'.join(f.readlines()[:5]))
            creator = [re.sub(r'\#\s+.*\s+by\s+(\w+)\s*.*', r'\1', x) for x in creator]

        # Notify OMFIT and modules developers with an email
        # if error occurred when user pushed on a GUI button,
        # if it is not a SyntaxError (likely that a user has edited a script),
        # if the user is not part of the developers (of OMFIT or of the module),
        # if the user has not disabled the report error and
        # if it is not the same error as the last error that occured
        # if it is not the user that created the file
        if (
            not isinstance(handled_exception, (doNotReportException, SyntaxError))
            and reportUsersErrorByEmail
            and OMFIT['MainSettings']['SETUP']['error_report']
            and OMFIT['MainSettings']['SETUP']['email'] not in developers
            and not lastSeen
            and os.environ['USER'] not in creator
        ):
            try:
                # Add MainSettings and module settings to the list of files
                OMFIT['MainSettings'].save()
                files.append(OMFIT['MainSettings'].filename)
                try:
                    if OMFITaux['lastRunModule'] != 'OMFIT':
                        eval(OMFITaux['lastRunModule'])['SETTINGS'].save()
                        files.append(eval(OMFITaux['lastRunModule'])['SETTINGS'].filename)
                except Exception:
                    pass

                message = (
                    'OMFIT project: {project}\n'
                    'OMFIT directory: {directory}\n'
                    'Git commit: {commit}\n'
                    'Python executable: {executable}\n'
                    'Hostname: {hostname}\n'
                    'Error in module location: {module}\n\n'
                    '====================================\n'
                    'Console output\n'
                    '====================================\n'
                    '{console}\n\n'
                    '===================================\n'
                    'Exception stack\n'
                    '====================================\n'
                    '{exception}\n\n'
                    ''.format(
                        project=str(OMFIT.filename),
                        directory=OMFITsrc,
                        commit=repo_str,
                        executable=sys.executable,
                        hostname=' | '.join(platform.uname()),
                        module=str('' if OMFITaux['lastRunModule'] == 'OMFIT' else OMFITaux['lastRunModule']),
                        # Note that .split('+------------------------------+')[-1] is done to avoid receiving:
                        # +------------------------------+     +------------------------------+
                        # | BELOW IS WHAT YOU WERE DOING | and | ABOVE IS WHAT YOU WERE DOING |
                        # +------------------------------+     +------------------------------+
                        console=OMFITaux['console'].get()[-10000:].split('+------------------------------+')[-1],
                        exception='\n'.join(excpStack),
                    )
                )

                # send email
                send_email(
                    to=developers,
                    fromm=OMFIT['MainSettings']['SETUP']['email'],
                    subject='OMFIT user error report' + moduleExceptionText,
                    message=message,
                    attachments=files,
                )
                printt('OMFIT user error report sent to < ' + ', '.join(developers) + ' >')
                OMFITaux['lastReportedUserError'] = excpStack

            except Exception as _excp1:
                printt('Problem sending error report: ' + repr(_excp1))

        # print simplified exception to console
        printe(simpleExcp)
        OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")

        return None, True


def _system(
    command_line,
    message='Processing...',
    fixedWidthDetails='',
    ignoreReturnCode=False,
    std_out=None,
    std_err=None,
    executable=None,
    quiet=False,
    progressFunction=None,
    extraButtons=None,
    noGUI=False,
):
    """
    :param command_line: command to be executed

    :param message: message to appear in the GUI

    :param fixedWidthDetails: further details to be formatted with a fixed width font, e.g., a script

    :param ignoreReturnCode: ignore return code of the command

    :param std_out: if a list is passed (e.g. []), the stdout of the program will be put there line by line

    :param std_err: if a list is passed (e.g. []), the stderr of the program will be put there line by line

    :param executable: shell executable, defaults to os.environ['SHELL'] and fallsback on default of subprocess.Popen()

    :param quiet: switch to turn ON/OFF print to console

    :param progressFunction: user function to which the std-out of the process is passed and returns values from 0 to 100 to indicate progress towards completion

    :param extraButtons: dictionary with key/function that is used to add extra buttons to the GUI. The function receives a dictionary with the process std_out and pid

    :param noGUI: do not show execution in GUI

    :return: return code of the spawned process
    """
    if os.name == 'nt' or int(os.environ.get('OMFIT_WINDOWS_SYSTEM', '0')):
        return _system_windows(
            command_line=command_line,
            message=message,
            fixedWidthDetails=fixedWidthDetails,
            ignoreReturnCode=ignoreReturnCode,
            std_out=std_out,
            std_err=std_err,
            executable=executable,
            quiet=quiet,
            progressFunction=progressFunction,
            extraButtons=extraButtons,
            noGUI=noGUI,
        )
    else:
        return _system_unix(
            command_line=command_line,
            message=message,
            fixedWidthDetails=fixedWidthDetails,
            ignoreReturnCode=ignoreReturnCode,
            std_out=std_out,
            std_err=std_err,
            executable=executable,
            quiet=quiet,
            progressFunction=progressFunction,
            extraButtons=extraButtons,
            noGUI=noGUI,
        )


def _system_unix(
    command_line, message, fixedWidthDetails, ignoreReturnCode, std_out, std_err, executable, quiet, progressFunction, extraButtons, noGUI
):
    import fcntl
    import select

    if executable is None:
        executable = os.environ['SHELL']

    if executable == 'OMFITbash':
        bashlink = OMFITbinsDir + os.sep + 'OMFITbash'
        if not os.path.exists(bashlink):
            with open(bashlink, 'w') as f:
                f.write('''#!/bin/bash\n/bin/bash -l "$@"\n''')
            os.chmod(bashlink, 0o700)
        executable = bashlink

    if extraButtons is None:
        extraButtons = {}

    try:
        # use original environmental variables before OMFIT messed with them
        backup_environ = {}
        for k in ['PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH']:
            if k in os.environ:
                backup_environ[k] = os.environ[k]
            os.environ[k] = os.environ.get(f'ORIGINAL_{k}', os.environ.get(k, ''))

        child = subprocess.Popen(
            command_line,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            executable=executable,
            preexec_fn=os.setsid,
        )
        # non blocking reading of buffers
        fcntl.fcntl(child.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(child.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

        gbl = {}
        gbl['std_out'] = ''
        gbl['pid'] = None

        if len(OMFITaux['prun_process']) or noGUI or (len(OMFITaux['pythonRunWindows']) and OMFITaux['pythonRunWindows'][-1] is None):
            gbl['std_out'], std_err_ = map(b2s, child.communicate())
            if std_out is not None:
                std_out.extend(gbl['std_out'].split('\n'))
            if std_err is not None:
                std_err.extend(std_err_.split('\n'))

        else:
            max_buffer_len = 10000000

            show = (OMFITaux['rootGUI'] is None or OMFITaux['console'].show) and not quiet

            printd(command_line, topic='framework')

            if OMFITaux['rootGUI'] is not None:
                tkMessage = tk.StringVar()
                if isinstance(message, str):
                    tkMessage.set(message)
                elif isinstance(message, CollectionsCallable):
                    tkMessage.set(message())
                tkDetails = tk.StringVar()
                if fixedWidthDetails:
                    tkDetails.set(fixedWidthDetails)

            def onKill():
                killed.set(True)
                top.update_idletasks()
                finished.set(True)
                top.update_idletasks()

            def onAbort():
                top.update_idletasks()
                aborted.set(True)
                finished.set(True)
                top.update_idletasks()

            def checkChild():

                if gbl['pid'] is None:
                    gbl['pid'] = child.pid

                elif child.poll() is not None:
                    try:
                        p['value'] = 100
                    except tk.TclError:
                        pass
                    finished.set(True)
                    if OMFITaux['rootGUI'] is not None:
                        top.destroy()
                    return

                elif select.select([child.stdout], [], [], 0)[0]:
                    try:
                        tmp = b2s(child.stdout.read())
                        # return output
                        gbl['std_out'] += tmp
                        gbl['std_out'] = gbl['std_out'][:max_buffer_len]
                        if progressFunction:
                            p['value'] = progressFunction(gbl['std_out'])
                        # output to console
                        if show:
                            tag_print(tmp, tag='PROGRAM_OUT', end='')
                    except IOError:
                        tmp = None

                if OMFITaux['rootGUI'] is not None and not finished.get():
                    if isinstance(message, CollectionsCallable):
                        tkMessage.set(message())
                    if OMFITaux['console'].show:
                        OMFITaux['rootGUI'].after(1, checkChild)
                    else:
                        OMFITaux['rootGUI'].after(100, checkChild)

            p = {'value': 0, 'maximum': 100}
            if OMFITaux['rootGUI'] is not None:
                try:
                    if OMFITaux['pythonRunWindows'][-1] is None:
                        raise RuntimeError('--')
                    top = ttk.Frame(OMFITaux['pythonRunWindows'][-1], borderwidth=2, relief=tk.GROOVE)
                    top.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH, padx=5, pady=5)
                except Exception:
                    top = tk.Toplevel(_topGUI(OMFITaux['rootGUI']))
                    top.transient(OMFITaux['rootGUI'])
                    top.protocol("WM_DELETE_WINDOW", 'break')
                    if isinstance(message, str):
                        top.wm_title(message)
                    elif isinstance(message, CollectionsCallable):
                        top.wm_title(message())

                top.update_idletasks()
                ttk.Label(top, textvar=tkMessage).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
                if fixedWidthDetails:
                    from utils_widgets import OMFITfont

                    fixedWidthDetailsText = tk.Text(
                        top, background=ttk.Style().lookup('TFrame', 'background'), wrap=tk.NONE, font=OMFITfont(size=-2, family='Courier')
                    )
                    fixedWidthDetailsText.pack(padx=5)
                    fixedWidthDetailsText.insert(1.0, tkDetails.get())
                    fixedWidthDetailsText.configure(
                        state='disabled', height=min([10, len(tkDetails.get().split('\n'))]), width=80, relief=tk.FLAT
                    )
                if progressFunction:
                    p = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='determinate')
                    p['value'] = 0
                    p['maximum'] = 100
                else:
                    p = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='indeterminate')
                    p.start()
                p.pack(padx=5, pady=5, expand=tk.NO, fill=tk.X)
                frm = ttk.Frame(top)
                ttk.Button(frm, text="Kill local", command=onKill, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
                for btt in list(extraButtons.keys()):
                    ttk.Button(frm, text=btt, command=lambda btt=btt: extraButtons[btt](gbl), takefocus=False).pack(
                        side=tk.LEFT, expand=tk.NO, fill=tk.X
                    )
                ttk.Button(frm, text="Abort", command=onAbort, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
                frm.pack(side=tk.TOP)
                top.update_idletasks()

            finished = tk.BooleanVar()
            finished.set(False)
            aborted = tk.BooleanVar()
            aborted.set(False)
            killed = tk.BooleanVar()
            killed.set(False)

            if OMFITaux['rootGUI'] is not None:
                checkChild()
                top.wait_variable(finished)
                top.destroy()
            else:
                while not finished.get():
                    checkChild()
                    sleep(0.1)

            if child.poll() is None and (aborted.get() or killed.get()):
                try:
                    os.killpg(gbl['pid'], signal.SIGTERM)
                    for k in range(20):
                        if child.poll() is not None:
                            break
                        if k == 10:
                            os.killpg(gbl['pid'], signal.SIGKILL)
                        sleep(0.1)
                except OSError:
                    pass

            # show the remaining standard output
            if std_out is not None or show:
                if select.select([child.stdout], [], [], 0)[0]:
                    try:
                        tmp = b2s(child.stdout.read())
                        gbl['std_out'] += tmp
                        gbl['std_out'] = gbl['std_out'][:max_buffer_len]
                        if std_out is not None:
                            std_out.extend(gbl['std_out'].split('\n'))
                        if show:
                            tag_print(tmp, tag='PROGRAM_OUT', end='')
                    except IOError:
                        tmp = None

            # show the standard error (all at the end)
            if std_err is not None or show:
                if select.select([child.stderr], [], [], 0)[0]:
                    try:
                        tmp = b2s(child.stderr.read())
                        if std_err is not None:
                            std_err_ = tmp[:max_buffer_len]
                            std_err.extend(std_err_.split('\n'))
                        if show:
                            tag_print(tmp, tag='PROGRAM_ERR', end='')
                    except IOError:
                        tmp = None

            if OMFITaux['rootGUI'] is not None:
                OMFITaux['rootGUI'].update_idletasks()
                OMFITaux['rootGUI'].focus_set()

            if killed.get():
                pass
            elif aborted.get():
                raise EndAllOMFITpython('\n\n---> Aborted by user <---\n\n')
            elif not ignoreReturnCode and child.poll() != 0:
                raise ReturnCodeException(
                    '\n\nReturn code was '
                    + str(child.poll())
                    + ' for command:\n\n'
                    + command_line
                    + '\n\nYou can ignore the return code by setting the keyword `ignoreReturnCode=True`'
                )

        return_val = child.poll()
        child.stderr.close()
        child.stdout.close()
        child.stdin.close()

    finally:
        # restore OMFIT-modified version of the environmental variables
        for k in ['PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH']:
            if k in backup_environ:
                os.environ[k] = backup_environ[k]
            elif k in os.environ:
                del os.environ[k]

    return return_val


def _system_windows(
    command_line, message, fixedWidthDetails, ignoreReturnCode, std_out, std_err, executable, quiet, progressFunction, extraButtons, noGUI
):
    if 'DYLD_LIBRARY_PATH' in os.environ:
        print('Removed DYLD_LIBRARY_PATH from os.environ')
        del os.environ['DYLD_LIBRARY_PATH']
    if executable is None:
        executable = os.environ.get('SHELL', None)

    if executable == 'OMFITbash':
        bashlink = OMFITbinsDir + os.sep + 'OMFITbash'
        if not os.path.exists(bashlink):
            with open(bashlink, 'w') as f:
                f.write('''#!/bin/bash\n/bin/bash -l "$@"\n''')
            os.chmod(bashlink, 0o700)
        executable = bashlink

    if extraButtons is None:
        extraButtons = {}

    kwarg = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, executable=executable)
    if os.name == 'nt':  # only for windows
        kwarg['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwarg['preexec_fn'] = os.setsid  # only for unix

    gbl = {}
    gbl['std_out'] = ''
    gbl['pid'] = None

    from threading import Thread
    from queue import Queue, Empty

    def enqueue_output(out, queue):
        while True:
            try:
                line = out.readline()
            except ValueError:
                break
            if not line:
                break
            queue.put(b2s(line))

    child = subprocess.Popen(command_line, shell=True, **kwarg)
    # non blocking reading of buffers
    # fcntl.fcntl(child.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
    # fcntl.fcntl(child.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

    # non blocking reading of buffers
    q_out = Queue()
    t_out = Thread(target=enqueue_output, args=(child.stdout, q_out))
    q_err = Queue()
    t_err = Thread(target=enqueue_output, args=(child.stderr, q_err))

    t_out.daemon = True  # thread dies with the program
    t_out.start()
    t_err.daemon = True  # thread dies with the program
    t_err.start()

    if len(OMFITaux['prun_process']) or noGUI or (len(OMFITaux['pythonRunWindows']) and OMFITaux['pythonRunWindows'][-1] is None and False):
        gbl['std_out'], std_err_ = map(b2s, child.communicate())
        if std_out is not None:
            std_out.extend(gbl['std_out'].split('\n'))
        if std_err is not None:
            std_err.extend(std_err_.split('\n'))

    else:
        max_buffer_len = 10000000

        show = (OMFITaux['rootGUI'] is None or OMFITaux['console'].show) and not quiet

        printd(command_line, topic='framework')

        if OMFITaux['rootGUI'] is not None:
            tkMessage = tk.StringVar()
            if isinstance(message, str):
                tkMessage.set(message)
            elif isinstance(message, CollectionsCallable):
                tkMessage.set(message())
            tkDetails = tk.StringVar()
            if fixedWidthDetails:
                tkDetails.set(fixedWidthDetails)

        def onKill():
            killed.set(True)
            top.update_idletasks()
            finished.set(True)
            top.update_idletasks()

        def onAbort():
            top.update_idletasks()
            aborted.set(True)
            finished.set(True)
            top.update_idletasks()

        def checkChild():

            if gbl['pid'] is None:
                gbl['pid'] = child.pid

            elif child.poll() is not None:
                try:
                    p['value'] = 100
                except tk.TclError:
                    pass
                finished.set(True)
                if OMFITaux['rootGUI'] is not None:
                    top.destroy()
                return
            else:

                try:
                    tmp = q_out.get_nowait()  # or q.get(timeout=.1)
                except Empty:
                    tmp = ''

                gbl['std_out'] += tmp
                gbl['std_out'] = gbl['std_out'][:max_buffer_len]
                if progressFunction:
                    p['value'] = progressFunction(gbl['std_out'])
                # output to console
                if show and tmp != '':
                    tag_print(tmp, tag='PROGRAM_OUT', end='')

            if OMFITaux['rootGUI'] is not None and not finished.get():
                if isinstance(message, CollectionsCallable):
                    tkMessage.set(message())
                if OMFITaux['console'].show:
                    OMFITaux['rootGUI'].after(1, checkChild)
                else:
                    OMFITaux['rootGUI'].after(100, checkChild)

        p = {'value': 0, 'maximum': 100}
        if OMFITaux['rootGUI'] is not None:
            try:
                if OMFITaux['pythonRunWindows'][-1] is None:
                    raise RuntimeError('--')
                top = ttk.Frame(OMFITaux['pythonRunWindows'][-1], borderwidth=2, relief=tk.GROOVE)
                top.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH, padx=5, pady=5)
            except Exception:
                top = tk.Toplevel(_topGUI(OMFITaux['rootGUI']))
                top.transient(OMFITaux['rootGUI'])
                top.protocol("WM_DELETE_WINDOW", 'break')
                if isinstance(message, str):
                    top.wm_title(message)
                elif isinstance(message, CollectionsCallable):
                    top.wm_title(message())

            top.update_idletasks()
            ttk.Label(top, textvar=tkMessage).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            if fixedWidthDetails:
                from utils_widgets import OMFITfont

                fixedWidthDetailsText = tk.Text(
                    top, background=ttk.Style().lookup('TFrame', 'background'), wrap=tk.NONE, font=OMFITfont(size=-2, family='Courier')
                )
                fixedWidthDetailsText.pack(padx=5)
                fixedWidthDetailsText.insert(1.0, tkDetails.get())
                fixedWidthDetailsText.configure(
                    state='disabled', height=min([10, len(tkDetails.get().split('\n'))]), width=80, relief=tk.FLAT
                )
            if progressFunction:
                p = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='determinate')
                p['value'] = 0
                p['maximum'] = 100
            else:
                p = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='indeterminate')
                p.start()
            p.pack(padx=5, pady=5, expand=tk.NO, fill=tk.X)
            frm = ttk.Frame(top)
            ttk.Button(frm, text="Kill local", command=onKill, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            for btt in list(extraButtons.keys()):
                ttk.Button(frm, text=btt, command=lambda btt=btt: extraButtons[btt](gbl), takefocus=False).pack(
                    side=tk.LEFT, expand=tk.NO, fill=tk.X
                )
            ttk.Button(frm, text="Abort", command=onAbort, takefocus=False).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            frm.pack(side=tk.TOP)
            top.update_idletasks()

        finished = tk.BooleanVar()
        finished.set(False)
        aborted = tk.BooleanVar()
        aborted.set(False)
        killed = tk.BooleanVar()
        killed.set(False)

        if OMFITaux['rootGUI'] is not None:
            checkChild()
            top.wait_variable(finished)
            top.destroy()
        else:
            while not finished.get():
                checkChild()
                sleep(0.1)

        if child.poll() is None and (aborted.get() or killed.get()):
            try:
                if os.name == 'nt':
                    child.send_signal(signal.SIGTERM)
                else:
                    os.killpg(gbl['pid'], signal.SIGTERM)
                for k in range(20):
                    if child.poll() is not None:
                        break
                    if k == 10:
                        if os.name == 'nt':
                            child.send_signal(signal.SIGKILL)
                        else:
                            os.killpg(gbl['pid'], signal.SIGKILL)
                    sleep(0.1)
            except OSError:
                pass

        # show the remaining standard output
        if std_out is not None or show:
            try:
                tmp = q_out.get_nowait()  # or q.get(timeout=.1)
            except Empty:
                tmp = ''

            gbl['std_out'] += tmp
            gbl['std_out'] = gbl['std_out'][:max_buffer_len]
            if std_out is not None:
                std_out.extend(gbl['std_out'].split('\n'))

            if show and tmp != '':
                tag_print(tmp, tag='PROGRAM_OUT', end='')

        # show the standard error (all at the end)
        if std_err is not None or show:

            try:
                tmp = q_err.get_nowait()  # or q.get(timeout=.1)
            except Empty:
                tmp = ''

            if std_err is not None:
                std_err_ = tmp[:max_buffer_len]
                std_err.extend(std_err_.split('\n'))
            if show and tmp != '':
                tag_print(tmp, tag='PROGRAM_ERR', end='')

        if OMFITaux['rootGUI'] is not None:
            OMFITaux['rootGUI'].update_idletasks()
            OMFITaux['rootGUI'].focus_set()

        if killed.get():
            pass
        elif aborted.get():
            raise EndAllOMFITpython('\n\n---> Aborted by user <---\n\n')
        elif not ignoreReturnCode and child.poll() != 0:
            raise ReturnCodeException(
                '\n\nReturn code was '
                + str(child.poll())
                + ' for command:\n\n'
                + command_line
                + '\n\nYou can ignore the return code by setting the keyword `ignoreReturnCode=True`'
            )

    return_val = child.poll()
    child.stderr.close()
    child.stdout.close()
    child.stdin.close()
    if t_out and t_out.is_alive():  # wait for thread to finish
        t_out.join(timeout=1)
    if t_err and t_err.is_alive():  # wait for thread to finish
        t_err.join(timeout=1)

    return return_val


def _xargs(command, data):
    data_string = ''
    commands = []
    data = copy.deepcopy(data)
    while len(data):
        data_string += data.pop() + ' '
        if not len(data) or (len(command) + len(data_string) + len(data[-1]) + len('\n echo Done ') + 9) > ARG_MAX:
            commands.append(re.sub(r'\{\}', data_string.strip(), command))
            data_string = ''
    if len(commands) > 1:
        printd('\n'.join(commands), topic='framework')
        commands = [item + '\necho Done ' + str(k + 1) + '/' + str(len(commands)) for k, item in enumerate(commands)]
    return commands


def _remote_upsync(server, local, remote, tunnel=None, ignoreReturnCode=False, quiet=False):
    if not len(local):
        return

    server0 = server
    tunnel0 = tunnel
    username, server, port = setup_ssh_tunnel(server0, tunnel0)

    if not isinstance(local, list):
        local = [local]
    remote = str(remote)

    local = [re.sub(' ', r'\ ', x) for x in local]
    local_str = ' '.join(local)
    if len(local_str) > 128:
        local_str = local_str[:64] + '...' + local_str[-64:]

    if not len(server):
        ret_code = 0
        if not quiet:
            printi('Local copy of: ' + ' '.join(local))
        if not os.path.exists(os.path.split(remote)[0]):
            os.makedirs(os.path.split(remote)[0])
        upsync = system_executable('cp') + ' -Rfp {} ' + remote
        upsync = _xargs(upsync, local)
        while len(upsync):
            command = upsync.pop(0)
            ret_code = _system(command, 'Local copy of:', fixedWidthDetails=local_str, ignoreReturnCode=True, noGUI=True)
            if ret_code != 0 and not ignoreReturnCode:
                break
    else:
        msg = 'Up-sync to ' + server0
        if tunnel0 is not None and tunnel0 != '':
            msg += ' (via ' + tunnel0 + ')'
        msg += ' of: ' + ' '.join(local)
        if not quiet:
            printi(msg)

        mkdir = (
            sshOptions()
            + controlmaster(username, server, port, server0)
            + " -Y -q -p "
            + port
            + " "
            + username
            + "@"
            + server
            + " 'mkdir -p "
            + remote
            + "'"
        )
        _system(mkdir, 'Building remote directory structure...', ignoreReturnCode=True)
        upsync = (
            "{path} {progress} --copy-links --update --inplace --compress --recursive -e '".format(**system_executable('rsync', True))
            + sshOptions()
            + controlmaster(username, server, port, server0)
            + " -q -p "
            + port
            + "' {} "
            + username
            + "@"
            + server
            + ":"
            + remote
        )
        upsync = _xargs(upsync, local)

        def progressFunction(out):
            n = float(len(upsync) + 1)
            try:
                return int(100 * segment / n + float(re.findall(' [0-9]+% ', out)[-1].strip(' %')) / n)
            except IndexError:
                return 0

        std_out = []
        std_err = []
        segment = 0
        while len(upsync):
            command = upsync.pop(0)
            ret_code = _system(
                command,
                'Up-Sync of:',
                fixedWidthDetails=local_str,
                ignoreReturnCode=True,
                progressFunction=progressFunction,
                quiet=True,
                std_out=std_out,
                std_err=std_err,
            )
            if ret_code != 0 and not ignoreReturnCode:
                break
            segment += 1

        if ret_code != 0:
            if not ignoreReturnCode:
                if ret_code == 255 and (server is not None and len(server)):
                    raise ReturnCodeException(
                        '\n\n' + command + '\n\n---> SSH connection to `%s` via `%s` was terminated <---\n\n' % (server0, tunnel0)
                    )
                else:
                    _streams['PROGRAM_ERR'].write(''.join(std_err) + '\n')
                    raise ReturnCodeException(
                        '\n\nReturn code was '
                        + str(ret_code)
                        + ' for UPSYNC command:\n\n'
                        + command
                        + '\n\nYou can ignore the return code by setting the keyword `ignoreReturnCode=True`'
                    )

    return ret_code


def _remote_downsync(server, remote, local, tunnel=None, ignoreReturnCode=False, quiet=False):
    if not len(remote):
        return

    server0 = server
    tunnel0 = tunnel
    username, server, port = setup_ssh_tunnel(server0, tunnel0)

    if not isinstance(remote, list):
        remote = [remote]
    local = str(local)

    remote = [re.sub(' ', r'\ ', x) for x in remote]
    remote_str = ' '.join(remote)
    if len(remote_str) > 128:
        remote_str = remote_str[:64] + '...' + remote_str[-64:]

    if not len(server):
        ret_code = 0
        if not quiet:
            printi('Local copy of: ' + ' '.join(remote))
        if not os.path.exists(os.path.split(local)[0]):
            os.makedirs(os.path.split(local)[0])
        downsync = system_executable('cp') + ' -Rfp {} ' + local
        downsync = _xargs(downsync, remote)
        while len(downsync):
            command = downsync.pop(0)
            ret_code = _system(command, 'Local copy of:', fixedWidthDetails=remote_str, ignoreReturnCode=True, noGUI=True)
            if ret_code != 0 and not ignoreReturnCode:
                break
    else:
        msg = 'Down-sync from ' + server0
        if tunnel0 is not None and tunnel0 != '':
            msg += ' (via ' + tunnel0 + ')'
        msg += ' of: ' + ' '.join(remote)
        if not quiet:
            printi(msg)
        if not os.path.exists(os.path.split(local)[0]):
            os.makedirs(os.path.split(local)[0])
        downsync = (
            "{path} {progress} --copy-links --update --inplace --compress --recursive -e '".format(**system_executable('rsync', True))
            + sshOptions()
            + controlmaster(username, server, port, server0)
            + " -q -p "
            + port
            + "' "
            + username
            + "@"
            + server
            + ":'{}' "
            + local
        )
        downsync = _xargs(downsync, remote)

        def progressFunction(out):
            n = float(len(downsync) + 1)
            try:
                return int(100 * segment / n + float(re.findall(' [0-9]+% ', out)[-1].strip(' %')) / n)
            except IndexError:
                return 0

        std_out = []
        std_err = []
        segment = 0
        while len(downsync):
            command = downsync.pop(0)
            ret_code = _system(
                command,
                'Down-Sync of:',
                fixedWidthDetails=remote_str,
                ignoreReturnCode=True,
                progressFunction=progressFunction,
                quiet=True,
                std_out=std_out,
                std_err=std_err,
            )
            if ret_code != 0 and not ignoreReturnCode:
                break
            segment += 1

        if ret_code != 0:
            if not ignoreReturnCode:
                if ret_code == 255 and (server is not None and len(server)):
                    raise ReturnCodeException(
                        '\n\n' + command + '\n\n---> SSH connection to `%s` via `%s` was terminated <---\n\n' % (server0, tunnel0)
                    )
                else:
                    _streams['PROGRAM_ERR'].write(''.join(std_err) + '\n')
                    raise ReturnCodeException(
                        '\n\nReturn code was '
                        + str(ret_code)
                        + ' for DOWNSYNC command:\n\n'
                        + command
                        + '\n\nYou can ignore the return code by setting the keyword `ignoreReturnCode=True`'
                    )

    return ret_code


def _shell_escape(command):
    return re.sub(r'([\$\\\`])', r'\\\1', command)


def _bang_commander(command, use_bang_command='OMFIT_run_command.sh', shell='bash', xterm=False):
    if use_bang_command is True:
        use_bang_command = 'OMFIT_run_command.sh'
    bang_command = '\n\\rm -f %s\n' % use_bang_command
    command = command.strip()

    if command.startswith('#!'):
        shell = re.sub('^#!', '', command.split('\n')[0])
        bang_command += (
            "\n\\cat << __b__MATCHING_EOF__b__ > %s \n" % use_bang_command + _shell_escape(command) + "\n__b__MATCHING_EOF__b__\n"
        )

    else:
        if shell == 'bash':
            shell = '/bin/bash -l'
        elif not shell.startswith('/'):
            shell = '/bin/' + shell
        bang_command += (
            "\n\\cat << __b__MATCHING_EOF__b__ > %s \n" % use_bang_command
            + _shell_escape('#!%s\n' % shell + command)
            + "\n__b__MATCHING_EOF__b__\n"
        )

    if xterm:
        bang_command += "chmod +x %s && xterm -e $PWD/%s" % (use_bang_command, use_bang_command)
    else:
        bang_command += "chmod +x %s && $PWD/%s" % (use_bang_command, use_bang_command)

    return bang_command, shell


def execute(
    command_line,
    interactive_input=None,
    ignoreReturnCode=False,
    std_out=None,
    std_err=None,
    quiet=False,
    arguments='',
    script=None,
    use_bang_command='OMFIT_run_command.sh',
    progressFunction=None,
    extraButtons=None,
):
    """
    This function allows execution of commands on the local workstation.

    :param command_line: string to be executed locally

    :param interactive_input: interactive input to be passed to the command

    :param ignoreReturnCode: ignore return code of the command

    :param std_out: if a list is passed (e.g. []), the stdout of the program will be put there line by line

    :param std_err: if a list is passed (e.g. []), the stderr of the program will be put there line by line

    :param quiet: print command to screen or not

    :param arguments: arguments that are passed to the `command_line`

    :param script: string with script to be executed.
                   `script` option substitutes `%s` with the automatically generated name of the script
                   if `script` is a list or a tuple, then the first item should be the script itself and the second should be the script name

    :param use_bang_command: Execute commands via `OMFIT_run_command.sh` script (useful to execute scripts within a given shell: #!/bin/...)
                             If `use_bang_command` is a string, then the run script will take that filename.
                             Notice that setting `use_bang_command=True` is not safe for multiple processes running in the same directory.

    :param progressFunction: user function to which the std-out of the process is passed and returns values from 0 to 100 to indicate progress towards completion

    :param extraButtons: dictionary with key/function that is used to add extra buttons to the GUI. The function receives a dictionary with the process std_out and pid

    :return: return code of the command
    """

    if extraButtons is None:
        extraButtons = {}

    # add open-terminal button to GUI
    def remote_terminal(kw, terminal_command):
        subprocess.Popen(terminal_command, shell=True)

    terminal_command = "xterm -e \"%s\"" % ('cd ' + os.getcwd() + ';exec ' + os.environ['SHELL'])
    extraButtons.setdefault('Open terminal', lambda kw={}, terminal_command=terminal_command: remote_terminal(kw, terminal_command))

    scriptName = ''
    if isinstance(script, (list, tuple)):
        scriptName = script[1]
        script = script[0]
    elif isinstance(script, OMFITascii):
        scriptName = os.path.split(script.filename)[1]
        with open(script.filename, 'r') as f:
            script = f.read()
    if isinstance(script, str):
        if not len(scriptName) and '%s' not in command_line:
            raise RuntimeError(
                '`script` option requires that you place `%s` in the command line location where you want the script filename to appear'
            )
        scriptFile = OMFITascii(scriptName)
        with open(scriptFile.filename, 'w') as f:
            f.write(script)
        os.chmod(scriptFile.filename, os.stat(scriptFile.filename).st_mode | stat.S_IEXEC)  # make the script executable by user
        if '%s' in command_line:
            command_line = command_line % (os.path.split(scriptFile.filename)[1])
        scriptFile.deploy()

    if isinstance(arguments, str):
        command_line = command_line + ' ' + arguments
    else:
        command_line = command_line + ' '.join(arguments)

    if interactive_input:
        command = (
            str(command_line.rstrip())
            + """ << __c__MATCHING_EOF__c__\n"""
            + _shell_escape(interactive_input)
            + """\n__c__MATCHING_EOF__c__\n"""
        )
    else:
        command = command_line

    bang_command = command
    shell = os.path.split(os.environ['SHELL'])[1]
    if use_bang_command:
        bang_command, shell = _bang_commander(command, use_bang_command, shell=shell)
    bang_command = "\\uname -n\n\\pwd\n\\echo local_PID=$$\n\\echo\n" + bang_command

    msg = 'Local execute'
    msg += ' of:\n' + command_line.strip()
    msg += ' in:\n' + os.getcwd()
    if not quiet:
        printi(msg)

    printd(bang_command, topic='execution')

    ret_code = _system(
        bang_command,
        message='Running locally:',
        fixedWidthDetails=command_line,
        ignoreReturnCode=ignoreReturnCode,
        std_out=std_out,
        std_err=std_err,
        executable='OMFITbash',
        quiet=quiet,
        progressFunction=progressFunction,
        extraButtons=extraButtons,
    )  # use /bin/bash because of syntax used by interactive_input
    return ret_code


@_available_to_userTASK
def remote_execute(
    server,
    command_line,
    remotedir,
    tunnel=None,
    interactive_input=None,
    ignoreReturnCode=False,
    std_out=None,
    std_err=None,
    quiet=False,
    arguments='',
    script=None,
    forceRemote=False,
    use_bang_command='OMFIT_run_command.sh',
    progressFunction=None,
    extraButtons=None,
    xterm=False,
):
    """
    This function allows execution of commands on remote workstations.
    It has the logic to check if the remote workstation is the local workstation and in that case executes locally.

    :param server: server to connect and execute the command

    :param command_line: string to be executed remotely (NOTE that if server='', the command is executed locally in the local directory)

    :param remotedir: remote working directory, if remote directory does not exist it will be created

    :param tunnel: tunnel to go through to connect to the server

    :param interactive_input: interactive input to be passed to the command

    :param ignoreReturnCode: ignore return code of the command

    :param std_out: if a list is passed (e.g. []), the stdout of the program will be put there line by line

    :param std_err: if a list is passed (e.g. []), the stderr of the program will be put there line by line

    :param quiet: print command to screen or not

    :param arguments: arguments that are passed to the `command_line`

    :param script: string with script to be executed.
                   `script` option substitutes `%s` with the automatically generated name of the script
                   if `script` is a list or a tuple, then the first item should be the script itself and the second should be the script name

    :param forceRemote: force remote connection even if server is localhost

    :param use_bang_command: execute commands via `OMFIT_run_command.sh` script (useful to execute scripts within a given shell: #!/bin/...)
                             If `use_bang_command` is a string, then the run script will take that filename.
                             Notice that setting `use_bang_command=True` is not safe for multiple processes running in the same directory.

    :param progressFunction: user function to which the std-out of the process is passed and returns values from 0 to 100 to indicate progress towards completion

    :param extraButtons: dictionary with key/function that is used to add extra buttons to the GUI. The function receives a dictionary with the process std_out and pid

    :param xterm: if True, launch command in its own xterm

    :return: return code of the command
    """

    if extraButtons is None:
        extraButtons = {}

    server0 = server
    tunnel0 = tunnel

    username, server, port = setup_ssh_tunnel(server0, tunnel0, forceRemote=forceRemote)

    remotedir = evalExpr(remotedir)

    if not server:
        oldDir = os.getcwd()
        if not os.path.exists(remotedir):
            os.makedirs(remotedir)
        os.chdir(remotedir)
        try:
            return execute(
                command_line,
                interactive_input=interactive_input,
                arguments=arguments,
                ignoreReturnCode=ignoreReturnCode,
                std_out=std_out,
                std_err=std_err,
                quiet=quiet,
                script=script,
                use_bang_command=use_bang_command,
                progressFunction=progressFunction,
                extraButtons=extraButtons,
            )
        finally:
            os.chdir(oldDir)

    scriptName = ''
    if isinstance(script, (list, tuple)):
        scriptName = script[1]
        script = script[0]
    elif isinstance(script, OMFITascii):
        scriptName = os.path.split(script.filename)[1]
        with open(script.filename, 'r') as f:
            script = f.read()
    if isinstance(script, str):
        if not len(scriptName) and '%s' not in command_line:
            raise RuntimeError(
                '`script` option requires that you place `%s` in the command line location where you want the script filename to appear'
            )
        scriptFile = OMFITascii(scriptName)
        with open(scriptFile.filename, 'w') as f:
            f.write(script)
        if '%s' in command_line:
            command_line = command_line % (os.path.split(scriptFile.filename)[1])

    if isinstance(arguments, str):
        command_line = command_line + ' ' + arguments
    else:
        command_line = command_line + ' '.join(arguments)

    if interactive_input:
        command = str(command_line) + ' << __a__MATCHING_EOF__a__\n' + _shell_escape(interactive_input) + '\n__a__MATCHING_EOF__a__\n'
    else:
        command = command_line

    sysinfo = remote_sysinfo(server0, tunnel0, quiet=quiet)

    bang_command = command
    shell = sysinfo['shell']
    if use_bang_command or xterm:
        bang_command, shell = _bang_commander(command, use_bang_command, shell=shell, xterm=xterm)

    header = "\\uname -n;\\pwd;\\echo remote_PID=$$;\\echo;"

    tmp_files = []

    def ssh_cd(inv, tty):
        if tty:
            tty = ' -t -t '
        else:
            tty = ''
        inv = "\nmkdir -p " + remotedir + "\ncd " + remotedir + "\n\n" + inv + "\n\n"
        tmp_files.append(tempfile._get_default_tempdir() + os.sep + next(tempfile._get_candidate_names()))
        with open(tmp_files[-1], 'w') as f:
            f.write(inv)
        printd(inv, topic='execution')
        ssh_inv = (
            'cat %s | ' % tmp_files[-1]
            + sshOptions()
            + controlmaster(username, server, port, server0)
            + tty
            + "-Y -q -p "
            + port
            + " "
            + username
            + "@"
            + server
            + " '%s%s -s'" % (header, shell)
        )
        printd(ssh_inv, topic='execution')
        return ssh_inv

    msg = 'Remote execute on ' + server0
    if tunnel0 is not None and tunnel0 != '':
        msg += ' (via ' + tunnel0 + ')'
    msg += ' of:\n' + command_line.strip()
    if not quiet:
        printi(msg)

    # add kill remote button to GUI
    def kill_remote(kw, kill_command):
        if kw['std_out'] is None or not len(kw['std_out']):
            printw('Remote process has not started yet. Nothing to kill.')
        else:
            found = re.search('remote_PID=[0-9]+', kw['std_out']).group()
            if not found:
                printw('Remote process has not started yet. Nothing to kill.')
                return
            kill_command = kill_command.format(PID=found.split('=')[1])
            subprocess.Popen(kill_command, shell=True)
            printi('Issued kill remote PID ' + found.split('=')[1])

    # send INT to the process group, allow 2 seconds, send KILL to the process group
    kill_command = (
        sshOptions()
        + controlmaster(username, server, port, server0)
        + " -q -p "
        + port
        + " "
        + username
        + "@"
        + server
        + " 'kill -INT -{PID}; sleep 2; kill -KILL -{PID}'"
    )
    extraButtons.setdefault('Kill remote', lambda kw={}, kill_command=kill_command: kill_remote(kw, kill_command))

    # add open-terminal button to GUI
    def remote_terminal(kw, terminal_command):
        subprocess.Popen(terminal_command, shell=True)

    terminal_command = "xterm -e \"%s\"" % (ssh_cd('exec ' + sysinfo['shell'], True))
    extraButtons.setdefault('Open terminal', lambda kw={}, terminal_command=terminal_command: remote_terminal(kw, terminal_command))

    # logic for setting TTY
    tty = not use_bang_command and interactive_input

    if isinstance(script, str):
        _remote_upsync(server0, scriptFile.filename, remotedir, tunnel=tunnel0, ignoreReturnCode=ignoreReturnCode)

    ret_code = _system(
        ssh_cd(bang_command, tty),
        message='Running remotely:',
        fixedWidthDetails=command_line,
        ignoreReturnCode=True,
        std_out=std_out,
        std_err=std_err,
        executable='OMFITbash',
        quiet=quiet,
        progressFunction=progressFunction,
        extraButtons=extraButtons,
    )  # use /bin/bash because of syntax used by interactive_input

    for file in tmp_files:
        if os.path.exists(file):
            os.remove(file)

    if ret_code != 0:
        if not ignoreReturnCode:
            if ret_code == 255:
                raise ReturnCodeException(
                    '\n\n' + command + '\n\n---> SSH connection to `%s` via `%s` was terminated <---\n\n' % (server0, tunnel0)
                )
            else:
                raise ReturnCodeException(
                    '\n\nReturn code was '
                    + str(ret_code)
                    + ' for REMOTE command:\n\n'
                    + ssh_cd(command, tty)
                    + '\n\nYou can ignore the return code by setting the keyword `ignoreReturnCode=True`'
                )

    return ret_code


@_available_to_userTASK
def remote_upsync(server, local, remote, tunnel=None, ignoreReturnCode=False, keepRelativeDirectoryStructure='', quiet=False):
    """
    Function to upload files/directories to remote server (possibly via tunnel connection)

    NOTE: this function relies on rsync.
    There is no way to arbitrarily rename files with rsync.
    All rsync can do is move files to a different directory.

    :param server: server to connect and execute the command

    :param local: local file(s) (string or list strings) to upsync

    :param remote: remote directory or file to save files to

    :param tunnel: tunnel to go through to connect to the server

    :param ignoreReturnCode: whether to ignore return code of the rsync command

    :param keepRelativeDirectoryStructure: string with common based directory of the locals files to be removed (usually equals `local_dir`)

    :param quiet: print command to screen or not

    :return: return code of the rsync command  (or True if keepRelativeDirectoryStructure and ignoreReturnCode and some rsync fail)
    """
    local = tolist(local)

    if keepRelativeDirectoryStructure:
        bases = [str(x).replace(str(keepRelativeDirectoryStructure), '').lstrip(os.sep) for x in local]
        base_dirs = set([os.path.split(x)[0] for x in bases])
        ret_codes = []
        for bd in base_dirs:
            individual = [str(keepRelativeDirectoryStructure) + os.sep + f for f in bases if os.path.split(f)[0] == bd]
            ret_codes.append(
                _remote_upsync(
                    server, individual, remote + os.sep + bd + os.sep, tunnel=tunnel, ignoreReturnCode=ignoreReturnCode, quiet=quiet
                )
            )
        return 0 if not np.any(ret_codes) else True

    else:
        return _remote_upsync(server, local, remote, tunnel=tunnel, ignoreReturnCode=ignoreReturnCode, quiet=quiet)


@_available_to_userTASK
def remote_downsync(server, remote, local, tunnel=None, ignoreReturnCode=False, keepRelativeDirectoryStructure='', quiet=False):
    """
    Function to download files/directories from remote server (possibly via tunnel connection)

    NOTE: this function relies on rsync.
    There is no way to arbitrarily rename files with rsync.
    All rsync can do is move files to a different directory.

    :param server: server to connect and execute the command

    :param remote: remote file(s) (string or list strings) to downsync

    :param local: local directory or file to save files to

    :param tunnel: tunnel to go through to connect to the server

    :param ignoreReturnCode: whether to ignore return code of the rsync command

    :param keepRelativeDirectoryStructure: string with common based directory of the remote files to be removed (usually equals `remote_dir`)

    :param quiet: print command to screen or not

    :param use_scp: (bool) If this flag is True remote_downsync will be executed with "scp" instead of "rsync". Use for increased download speed.  (default: False)

    :return: return code of the rsync command (or True if keepRelativeDirectoryStructure and ignoreReturnCode and some rsync fail)
    """
    remote = tolist(remote)

    if keepRelativeDirectoryStructure:
        bases = [str(x).replace(str(keepRelativeDirectoryStructure), '').lstrip(os.sep) for x in remote]
        base_dirs = set([os.path.split(x)[0] for x in bases])
        ret_codes = []
        for bd in base_dirs:
            individual = [str(keepRelativeDirectoryStructure) + os.sep + f for f in bases if os.path.split(f)[0] == bd]
            ret_codes.append(
                _remote_downsync(
                    server, individual, local + os.sep + bd + os.sep, tunnel=tunnel, ignoreReturnCode=ignoreReturnCode, quiet=quiet
                )
            )
        return 0 if not np.any(ret_codes) else True

    else:
        return _remote_downsync(server, remote, local, tunnel=tunnel, ignoreReturnCode=ignoreReturnCode, quiet=quiet)


def mdsvalue(server, treename=None, shot=None, TDI=None):
    """
    :param server: MDS+ server to connect to

    :param treename: name of the MDS+ tree

    :param shot: shot number

    :param TDI: TDI string to be executed

    :return: result of TDI command
    """
    server, treename, shot = OMFITmdsObjects(server, treename, shot).interpret_id()
    tunneled_server = tunneled_MDSserver(server, quiet=True)
    tmp = omfit_mds.OMFITmdsConnectionBase().mdsvalue(tunneled_server, treename, shot, TDI)
    tmp = np.atleast_1d(tmp)
    if tmp.dtype.char.lower() in ['s', 'u']:
        return '\n'.join(list(map(b2s, tmp)))
    elif tmp.size == 1:
        return tmp[0]
    else:
        return tmp


@_available_to_userTASK
class IDL(object):
    """
    This class provides a live IDL session via the pidly module: https://pypi.python.org/pypi/pyIDL/
    In practice this class wraps the pidly.IDL session so that it can handle SERVERS remote connections (including tunneling) and directory management the OMFIT way.
    The IDL executable is taken from the `idl` entry of this server under OMFIT['MainSettings']['SERVER'].

    Local and remote working directories are specified in root['SETTINGS']['SETUP']['workDir'] and root['SETTINGS']['REMOTE_SETUP']['workDir'].

    Server and tunnel are specified in root['SETTINGS']['REMOTE_SETUP']['server'] and root['SETTINGS']['REMOTE_SETUP']['tunnel'].

    If the tunnel is an empty string, the connection to the remote server is direct. If server is an empty string, everything will occur locally and the remote working directory will be ignored.

    :param module_root: root of the module (e.g. `root`)

    :param server: override module server

    :param tunnel: override module tunnel

    :param executable: override the executable is taken from the `idl` entry of this server under OMFIT['MainSettings']['SERVER'].

    :param workdir: override module local working directory

    :param remotedir: override module remote working directory

    :param clean: clear local/remote working directories

        * "local": clean local working directory only

        * "local_force": force clean local working directory only

        * "remote": clean remote working directory only

        * "remote_force": force clean remote working directory only

        * True: clean both

        * "force": force clean both

        * False: clean neither [DEFAULT]

    >>> idl=OMFITx.IDL(OMFIT['EFIT'])
    >>> idl('$pwd')
    >>> idl('x = total([1, 1], /int)')
    >>> print(idl.x)
    >>> tmp=OMFITgeqdsk(OMFITsrc+'/../samples/g133221.01000')
    >>> idl.upsync([tmp])
    >>> idl.downsync(['g133221.01000'])
    """

    def __init__(self, module_root, server=None, tunnel=None, executable=None, workdir=None, remotedir=None, clean=False):

        if server is None:
            server = str(module_root['SETTINGS']['REMOTE_SETUP']['server'])
        if tunnel is None:
            tunnel = str(module_root['SETTINGS']['REMOTE_SETUP']['tunnel'])
        if executable is None:
            try:
                executable = SERVER[SERVER(server)]['idl']
                # pexpect can choke on 'module load' on the local server
                if is_localhost(server):
                    executable = executable.split(';')[-1]
            except Exception:
                raise OMFITexception(
                    "Server " + server + " does not have `idl` setup. You may need to update OMFIT['MainSettings']['SERVER'] to fix this."
                )
        if remotedir is None:
            remotedir = str(module_root['SETTINGS']['REMOTE_SETUP']['workDir'])
        if workdir is None:
            workdir = str(module_root['SETTINGS']['SETUP']['workDir'])

        server0 = server
        tunnel0 = tunnel
        username, server, port = setup_ssh_tunnel(server0, tunnel0)

        self._OMFITserver = server0
        self._OMFITtunnel = tunnel0

        initWorkdir(module_root, clean=clean, server=server0, tunnel=tunnel0, workdir=workdir, remotedir=remotedir)

        def ssh_cd(inv):
            source = ''
            if len(sysinfo['login']):
                source = 'source ' + '\nsource '.join(sysinfo['login']) + '\n'
            return (
                sshOptions()
                + controlmaster(username, server, port, server0)
                + " -t -t -Y -q -p "
                + port
                + " "
                + username
                + "@"
                + server
                + " '"
                + source
                + "mkdir -p "
                + remotedir
                + "\ncd "
                + remotedir
                + "\n\n"
                + inv
                + "\n\n'"
            )

        if len(server):
            sysinfo = remote_sysinfo(self._OMFITserver, self._OMFITtunnel)
            executable = ssh_cd(executable)

        self.idl = pidly.IDL(executable)

    def upsync(self, inputs=[], keepRelativeDirectoryStructure=False, ignoreReturnCode=False, quiet=False):
        '''
        Function used to upload files from the local working directory to remote IDL directory

        :param inputs: list of input objects or path to files, which will be deployed in the local or remote working directory.
                       To deploy objects with a different name one can specify tuples (inputObject,'deployName')

        :param ignoreReturnCode: whether to ignore return code of the rsync command

        :param quiet: print command to screen or not
        '''
        self.idl('CD, Current=OMFIT_idl_pwd')
        remotedir = str(self.idl.OMFIT_idl_pwd) + '/'
        upsyncFiles = []
        for item in inputs:
            if isinstance(item, list) or isinstance(item, tuple):
                item[0].deploy(item[1])
                upsyncFiles.append(item[1])
            elif hasattr(item, 'deploy'):
                item.deploy()
                upsyncFiles.append(os.path.split(item.filename)[1])
            elif isinstance(item, str):
                shutil.copy2(item, os.path.split(item)[1])
                upsyncFiles.append(os.path.split(item)[1])

        remote_upsync(
            server=self._OMFITserver,
            local=upsyncFiles,
            remote=remotedir,
            tunnel=self._OMFITtunnel,
            ignoreReturnCode=ignoreReturnCode,
            keepRelativeDirectoryStructure=keepRelativeDirectoryStructure,
            quiet=quiet,
        )

    def downsync(self, outputs=[], ignoreReturnCode=False, keepRelativeDirectoryStructure=False, quiet=False):
        '''
        Function used to download files from the remote IDL directory to the local working directory

        :param outputs: list of output files which will be fetched from the remote directory

        :param keepRelativeDirectoryStructure: [True/False] keep relative directory structure of the remote files

        :param ignoreReturnCode: whether to ignore return code of the rsync command

        :param quiet: print command to screen or not
        '''
        self.idl('CD, Current=OMFIT_idl_pwd')
        remotedir = str(self.idl.OMFIT_idl_pwd) + '/'
        downsyncFiles = [remotedir + file for file in outputs]
        if outputs:
            if keepRelativeDirectoryStructure:
                remote_downsync(
                    server=self._OMFITserver,
                    remote=downsyncFiles,
                    local='./',
                    tunnel=self._OMFITtunnel,
                    ignoreReturnCode=ignoreReturnCode,
                    keepRelativeDirectoryStructure=remotedir,
                    quiet=quiet,
                )
            else:
                remote_downsync(
                    server=self._OMFITserver,
                    remote=downsyncFiles,
                    local='./',
                    tunnel=self._OMFITtunnel,
                    ignoreReturnCode=ignoreReturnCode,
                    keepRelativeDirectoryStructure=False,
                    quiet=quiet,
                )

    def __getattr__(self, attr):
        if attr in ['__tree_repr__', '_OMFITcopyOf', '_OMFITparent', '_OMFITkeyName', 'dynaLoad', 'dynaSave', '__len__', '__getitem__']:
            raise AttributeError('bad attribute `%s`' % attr)
        else:
            tmp = getattr(self.idl, attr)
            if tmp is None:
                raise AttributeError('bad attribute `%s`' % attr)
            return tmp

    def __call__(self, *args, **kw):
        if not len(args) and not len(kw):
            return
        return self.idl(*args, **kw)


# ---------------------------
# module tool functions
# ---------------------------
@_available_to_userTASK
def initWorkdir(module_root, server=None, tunnel=None, workdir=None, remotedir=None, clean=True, quiet=False):
    """
    High level function to simplify initialization of directories within a module. This function will:
    1) Create and clear local and remote working directories
    2) Change directory to local working directory

    Server and tunnel are specified in root['SETTINGS']['REMOTE_SETUP']['server'] and root['SETTINGS']['REMOTE_SETUP']['tunnel']

    Local and remote working directories are specified in root['SETTINGS']['SETUP']['workDir'] and root['SETTINGS']['REMOTE_SETUP']['workDir']

    :param module_root: root of the module

    :param server: string that overrides module server

    :param tunnel: string that overrides module tunnel

    :param workdir: string that overrides module local working directory

    :param remotedir: string that overrides module remote working directory

    :param clean: clear local/remote working directories

        * "local": clean local working directory only

        * "local_force": force clean local working directory only

        * "remote": clean remote working directory only

        * "remote_force": force clean remote working directory only

        * True: clean both

        * "force": force clean both

        * False: clean neither

    :param quiet: print command to screen or not

    :return: strings for local and remote directories (None if there was a problem in either one)
    """
    if workdir is None:
        workdir = module_root['SETTINGS']['SETUP']['workDir']
    if workdir.strip() == OMFITtmpDir:
        raise ValueError('Setting workdir as OMFITtmpDir is a bad idea and would lead to problems')
    workdir = str(workdir)
    if remotedir is None:
        remotedir = module_root['SETTINGS']['REMOTE_SETUP']['workDir']
    remotedir = str(remotedir)

    if clean is False:
        cleanLocal = False
        cleanRemote = False
    elif clean is True or (isinstance(clean, str) and 'force' == clean.lower()):
        cleanLocal = True
        cleanRemote = True
    elif isinstance(clean, str) and 'remote' in clean.lower():
        cleanLocal = False
        cleanRemote = True
    elif isinstance(clean, str) and 'local' in clean.lower():
        cleanLocal = True
        cleanRemote = False
    else:
        raise AttributeError('`clean` argument not valid')

    # safety mechanism to detect if workdir and remotedir coincide.
    # if that is the case, delete files only if both cleanRemote and cleanLocal are True
    if os.path.exists(workdir) and os.path.exists(remotedir):
        tmpfile = omfit_hash(str(time.time()), 10)
        with open(workdir + os.sep + tmpfile, 'w') as f:
            pass
        try:
            with open(remotedir + os.sep + tmpfile, 'r') as f:
                pass
            if not quiet:
                printi('Local and remote directory coincide!')
            cleanAtAll = bool(cleanLocal) & bool(cleanRemote)
            cleanLocal = cleanAtAll
            cleanRemote = cleanAtAll
        except Exception:
            pass
        os.remove(workdir + os.sep + tmpfile)

    if cleanLocal and os.path.exists(workdir):
        if 'OMFIT' in workdir or (isinstance(clean, str) and 'force' in clean.lower()):
            if not quiet:
                printi('Clearing local directory: ' + workdir)
            for dirTop, dirs, files in os.walk(workdir):
                for f in files:
                    os.unlink(os.path.join(dirTop, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(dirTop, d), ignore_errors=True)
        else:
            raise RuntimeError(
                f'''
This is a safety measure. The local working directory {workdir} does not contain the word "OMFIT" in it.
To allow clearing of local directory data, add the word "OMFIT" as part of the path, or set clean="local_force".'''.strip()
            )
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    if not quiet:
        printi('Changed to working directory: ' + workdir)
    os.chdir(workdir)

    if server is None:
        server = str(module_root['SETTINGS']['REMOTE_SETUP']['server'])
    if tunnel is None:
        tunnel = str(module_root['SETTINGS']['REMOTE_SETUP']['tunnel'])

    # assume that remote server is always unix
    noalias = '' if os.name == 'nt' else '\\'
    mkdir = 'mkdir ' if os.name == 'nt' and is_localhost(server) else 'mkdir -p '

    if cleanRemote:
        if 'OMFIT' in remotedir or (isinstance(clean, str) and 'force' in clean.lower()):
            if not quiet:
                printi('Clearing remote directory: ' + remotedir)
            # steps to make sure that the remote filesystem is writable by the user
            # and that future remote_execute calls can `cd` to the remote directory:
            # 1) create the directory
            # 2) touch a file in it
            # 3) remove all file in the directory
            remote_execute(
                server,
                noalias
                + mkdir
                + remotedir
                + ';'
                + noalias
                + 'echo > '
                + remotedir
                + os.sep
                + utils_base.now("touch_%Y-%m-%d__%H_%M_%S__%f")
                + ';'
                + noalias
                + 'rm -rf '
                + remotedir
                + os.sep
                + '*',
                '.' + os.sep,
                tunnel,
                ignoreReturnCode=True,
                quiet=True,
                use_bang_command=False,
            )
        else:
            raise RuntimeError(
                'This is a safety measure. The remote working directory '
                + remotedir
                + ' does not contain the word "OMFIT" in it.\nTo allow clearing of remote directory data, add the word "OMFIT" as part of the path, or set clean="remote_force".'
            )
    else:
        remote_execute(server, noalias + mkdir + remotedir, '.' + os.sep, tunnel, ignoreReturnCode=True, quiet=True, use_bang_command=False)

    return workdir, remotedir


@_available_to_userTASK
def executable(
    module_root=None,
    inputs=[],
    outputs=[],
    clean=True,
    interactive_input=None,
    server=None,
    tunnel=None,
    executable=None,
    workdir=None,
    remotedir=None,
    ignoreReturnCode=True,
    std_out=None,
    std_err=None,
    quiet=False,
    queued=False,
    keepRelativeDirectoryStructure=True,
    arguments='',
    script=None,
    forceRemote=False,
    progressFunction=None,
    use_bang_command='OMFIT_run_command.sh',
    extraButtons=None,
    xterm=False,
    clean_after=False,
):
    """
    High level function that simplifies local/remote execution of software within a module.

    This function will:
    1. cd to the local working directory
    2. Clear local/remote working directories [True] by default
    3. Deploy the the "input" objects to local working directory
    4. Upload files them remotely
    5. Executes the software
    6. Download "output" files to local working directory

    Executable command is specified in root['SETTINGS']['SETUP']['executable']

    Local and remote working directories are specified in root['SETTINGS']['SETUP']['workDir'] and root['SETTINGS']['REMOTE_SETUP']['workDir'].

    Server and tunnel are specified in root['SETTINGS']['REMOTE_SETUP']['server'] and root['SETTINGS']['REMOTE_SETUP']['tunnel'].

    If the tunnel is an empty string, the connection to the remote server is direct. If server is an empty string, everything will occur locally and the remote working directory will be ignored.

    :param module_root: root of the module (e.g. `root`) used to set default values for 'executable','server','tunnel','workdir', 'remotedir'
                        if `module_root` is None or `module_root` is OMFIT then
                        'executable','server','tunnel','workdir', 'remotedir' must be specified

    :param inputs: list of input objects or path to files, which will be deployed in the local or remote working directory.
                   To deploy objects with a different name one can specify tuples (inputObject,'deployName')

    :param outputs: list of output files which will be fetched from the remote directory

    :param clean: clear local/remote working directories

        * "local": clean local working directory only

        * "local_force": force clean local working directory only

        * "remote": clean remote working directory only

        * "remote_force": force clean remote working directory only

        * True: clean both [DEFAULT]

        * "force": force clean both

        * False: clean neither

    :param arguments: arguments which will be passed to the executable

    :param interactive_input: interactive input to be passed to the executable

    :param server: override module server

    :param tunnel: override module tunnel

    :param executable: override module executable

    :param workdir: override module local working directory

    :param remotedir: override module remote working directory

    :param ignoreReturnCode: ignore return code of executable

    :param std_out: if a list is passed (e.g. []),
        the stdout of the program will be put there line by line;
        if a string is passed and bool(queued), this should indicate
        the path of the file that gives the stdout of the queued job

    :param std_err: if a list is passed (e.g. []),
        the stderr of the program will be put there line by line;
        if a string is passed and bool(queued), this should indicate
        the path of the file that gives the stdout of the queued job

    :param quiet: if True, suppress output to the command box

    :param keepRelativeDirectoryStructure: [True/False] keep relative directory structure of the remote files

    :param script: string with script to be executed. `script` option requires
        `%s` in the command line location where you want the script filename to appear
        if `script` is a list or a tuple, then the first item should be the script itself and the second should be the script name

    :param forceRemote: force remote connection even if server is localhost

    :param progressFunction: user function to which the std-out of the process is
        passed and returns values from 0 to 100 to indicate progress towards completion

    :param queued: If cast as bool is True, invokes manage_job, using queued as
        qsub_findID keyword of manage_job, and also takes over std_out and std_err

    :param use_bang_command: Execute commands via `OMFIT_run_command.sh` script (useful to execute scripts within a given shell: #!/bin/...)
                             If `use_bang_command` is a string, then the run script will take that filename.
                             Notice that setting `use_bang_command=True` is not safe for multiple processes running in the same directory.

    :param extraButtons: dictionary with key/function that is used to add extra buttons to the GUI. The function receives a dictionary with the process std_out and pid

    :param xterm: if True, launch the command in its own xterm

    :param clean_after: (bool) If this flag is True, the remote directory will be removed once the outputs have been transferred to the local working directory. The remote directory have OMFIT in it's name. (default: False)

    :param use_scp: (bool) If this flag is True, the remote downsync of data will use the "scp" command instead of "rsync". This should be used for increased download speed. (default: False)

    :return: return code of the command
    """
    if extraButtons is None:
        extraButtons = {}

    # if module_root is not set
    if module_root is None or module_root is OMFIT:

        from omfit_classes.omfit_python import OMFITworkDir

        if is_localhost(server):
            server = ''
            tunnel = ''

        # remotedir as relative path
        if remotedir is None and isinstance(workdir, str) and not workdir.strip().startswith(os.sep):
            remotedir = OMFITworkDir(root='out_of_module_runs' + os.sep + workdir, server=SERVER(server))
        elif isinstance(remotedir, str) and not remotedir.strip().startswith(os.sep):
            remotedir = OMFITworkDir(root='out_of_module_runs' + os.sep + remotedir, server=SERVER(server))

        if is_localhost(server) and workdir is None:
            workdir = remotedir
        if workdir is None:
            raise ValueError('OMFITx.executable: `workdir` must be specified (either as an absolute or relative path)')
        # workdir as relative path
        elif not workdir.strip().startswith(os.sep):
            workdir = OMFITworkDir(root='out_of_module_runs' + os.sep + workdir, server=SERVER(''))

        if isinstance(remotedir, str):
            pass
        elif is_localhost(server) and remotedir is None:
            remotedir = workdir
        else:
            raise ValueError('OMFITx.executable: `remotedir` must be specified (either as an absolute or relative path)')

    else:
        # use module_root as defaults
        if server is None:
            server = str(module_root['SETTINGS']['REMOTE_SETUP']['server'])
        if tunnel is None:
            tunnel = str(module_root['SETTINGS']['REMOTE_SETUP']['tunnel'])
        if executable is None:
            executable = str(module_root['SETTINGS']['SETUP']['executable'])
        if remotedir is None:
            remotedir = str(module_root['SETTINGS']['REMOTE_SETUP']['workDir'])
        if workdir is None:
            workdir = str(module_root['SETTINGS']['SETUP']['workDir'])

    # check that the minimum info are set
    invalid = []
    for item in ['executable', 'server', 'tunnel', 'workdir', 'remotedir']:
        if is_none(locals()[item]):
            invalid.append(item)
    if invalid:
        raise OMFITexception('OMFITx.executable: %s must be set and not None' % invalid)

    # initialize local/remote directory
    initWorkdir(module_root, clean=clean, server=server, tunnel=tunnel, workdir=workdir, remotedir=remotedir, quiet=quiet)

    # deploy inputs and generate upsync and downsync file lists
    upsyncFiles = []
    for item in inputs:
        if isinstance(item, list) or isinstance(item, tuple):
            item[0].deploy(item[1])
            upsyncFiles.append(item[1])
        elif hasattr(item, 'deploy'):
            item.deploy()
            upsyncFiles.append(os.path.split(item.filename)[1])
        elif isinstance(item, str):
            upsyncFiles.append(item)
    downsyncFiles = [remotedir + file for file in outputs]

    # upload inputs
    if upsyncFiles:
        remote_upsync(
            server=server,
            local=upsyncFiles,
            remote=remotedir,
            tunnel=tunnel,
            quiet=quiet,
            ignoreReturnCode=ignoreReturnCode,
            keepRelativeDirectoryStructure=os.getcwd(),
        )

    # handle batch jobs
    if queued:
        if std_out is None:
            std_out_fn = ''
        else:
            std_out_fn = remotedir + '/' + std_out
        if std_err is None:
            std_err_fn = ''
        else:
            std_err_fn = remotedir + '/' + std_err
        std_out = []
        std_err = []

    # remote execute
    ret_code = remote_execute(
        server,
        executable,
        remotedir,
        tunnel,
        interactive_input=interactive_input,
        ignoreReturnCode=ignoreReturnCode,
        std_out=std_out,
        std_err=std_err,
        quiet=quiet,
        arguments=arguments,
        script=script,
        forceRemote=forceRemote,
        use_bang_command=use_bang_command,
        progressFunction=progressFunction,
        extraButtons=extraButtons,
        xterm=xterm,
    )

    # wait for batch job to finish
    if queued:
        if isinstance(queued, str) and queued != 'quiet':
            job = manage_job(module_root, std_out, server=server, tunnel=tunnel, remotedir=remotedir, qsub_findID=queued)
        else:
            job = manage_job(module_root, std_out, server=server, tunnel=tunnel, remotedir=remotedir)
        if queued == 'quiet':
            job.wait()
        else:
            try:
                job.wait_print(std_out_fn, std_err_fn, extraButtons=extraButtons)
            except Exception:
                if ignoreReturnCode:
                    pass
                else:
                    raise

    # download outputs
    if outputs:
        if keepRelativeDirectoryStructure:
            remote_downsync(
                server=server,
                remote=downsyncFiles,
                local='./',
                tunnel=tunnel,
                quiet=quiet,
                ignoreReturnCode=ignoreReturnCode,
                keepRelativeDirectoryStructure=remotedir,
            )
        else:
            remote_downsync(
                server=server,
                remote=downsyncFiles,
                local='./',
                tunnel=tunnel,
                quiet=quiet,
                ignoreReturnCode=ignoreReturnCode,
                keepRelativeDirectoryStructure=False,
            )

    # clean up remotedir after file transfer
    # presumably all outputs are now in the localhost workdir, from which they will be loaded into OMFIT
    if clean_after and not (is_localhost(server) and workdir == remotedir):
        if 'OMFIT' in remotedir:
            if not quiet:
                printi('Clearing remote directory: ' + remotedir)
            remote_execute(server, 'rm -rf ' + remotedir, './', tunnel, ignoreReturnCode=False, quiet=True, use_bang_command=False)
        else:
            raise RuntimeError(
                'This is a safety measure. The remote working directory '
                + remotedir
                + ' does not contain the word "OMFIT" in it.\nTo allow clearing of remote directory data, add the word "OMFIT" as part of the path, or set clean="remote_force".'
            )

    # handle errors
    if not ignoreReturnCode:
        for item in outputs:
            if not ignoreReturnCode and not len(_glob(item)):
                raise RuntimeError('Output file ' + item + ' not found in local working directory: ' + str(workdir))

    return ret_code


_executable = executable


@_available_to_userTASK
def remote_python(
    module_root=None,
    python_script=None,
    target_function=None,
    namespace={},
    executable=None,
    forceRemote=False,
    pickle_protocol=2,
    clean_local=False,
    **kw,
):
    r"""
    Execute a Python target_function that is self-contained in a Python `python_script`,
    Useful to execute a Python module as a separate process on a local (or remote) workstation.
    This fuction relies on the OMFITx.executable function and additional keyword arguments are passed to it.

    :param module_root: root of the module (e.g. `root`) used to set default values for 'executable','server','tunnel','workdir', 'remotedir'
                        if `module_root` is None or `module_root` is OMFIT then
                        'executable','server','tunnel','workdir', 'remotedir' must be specified

    :param python_script: OMFITpythonTask (or string) to execute

    :param target_function: function in the `python_script` that will be called

    :param namespace: dictionary with variables passed to the target_function

    :param executable: python executable (if `None` then is set based on SERVER)

    :param forceRemote: force remote connection even if server is localhost

    :param pickle_protocol: pickle protocol version (use 2 for Python2/3 compatibility)

    :param clean_local: (bool) If Flag is True, this cleans and deletes the local working directory after result to be returned has been loaded into memory. The directory must have OMFIT somewhere in the name as a safety measure. (default: False).

    :param \**kw: additional arguments are passed to the underlying OMFITx.executable function

    :return: returns the output of the `target_function`
    """

    # sanity check
    if not python_script:
        raise ValueError("`python_script` must be specified.")

    inputs = kw.pop('inputs', [])
    outputs = kw.pop('outputs', [])

    # must evaluate expressions in namespace so that the pickle file can be evaluated on a
    # remote server independently of whether OMFIT is available there or not
    namespace_eval = {}
    for item in namespace:
        namespace_eval[item] = evalExpr(namespace[item])

    # pickle file with input namespace
    namespace_file = OMFITascii('_namespace_in.pkl')
    with open(namespace_file.filename, 'wb') as f:
        pickle.dump(namespace_eval, f, protocol=pickle_protocol)

    if isinstance(python_script, OMFITascii):
        with open(python_script.filename, 'r') as f:
            script_text = f.read()
        script_file = os.path.split(python_script.filename)[1]
    elif isinstance(python_script, str):
        script_text = python_script
        script_file = 'python_script.py'
    else:
        script_text, script_file = python_script

    script_text += '''

if __name__ == '__main__':
    import pickle
    import os
    import traceback

    starting_directory = os.getcwd()

    with open(starting_directory + os.sep + '_namespace_in.pkl', 'rb') as f:
        data = pickle.load(f)

    try:
        excp = None
        out = {target_function}(**data)
    except Exception as _excp:
        excp = _excp
        out = ('OMFIT remote python exception', _excp, traceback.format_exc().strip())

    with open(starting_directory + os.sep + '_namespace_out.pkl', 'wb') as f:
        pickle.dump(out, f, {pickle_protocol})

    if excp:
        raise(excp)
'''.format(
        target_function=target_function, pickle_protocol=pickle_protocol
    )

    script_main = OMFITascii(script_file, fromString=script_text)

    if executable is None:
        if module_root is None:
            server = ''
        else:
            server = module_root['SETTINGS']['REMOTE_SETUP']['server']

        server = kw.get('server', server)
        if is_localhost(server):
            executable = sys.executable + ' -u ' + script_file
        else:
            executable = SERVER[server].get('python', 'python') + ' -u ' + script_file

    elif '%s' in executable and not kw.get('script'):
        executable = executable % script_file

    _executable(
        module_root=module_root,
        executable=executable,
        inputs=inputs + [namespace_file, script_main],
        outputs=outputs + ['_namespace_out.pkl'],
        forceRemote=forceRemote,
        **kw,
    )

    with open('_namespace_out.pkl', 'rb') as f:
        result = pickle.load(f)
    if isinstance(result, tuple) and len(result) == 3 and result[0] == 'OMFIT remote python exception':
        raise result[1].__class__(result[2])
    if clean_local and ('workDir' in kw and kw['workDir'] is not None and 'OMFIT' in kw['workDir']):
        os.chdir(str(OMFITcwd))
        shutil.rmtree(str(kw['workDir']))
    return result


@_available_to_userTASK
class manage_job(object):
    def __init__(
        self,
        module_root,
        qsub_job,
        server=None,
        tunnel=None,
        remotedir=None,
        qsub_findID=r'(?i)\'[^\']+\'|"[^"]+"|([0-9]{3,}[\.\w-]*)\s*',
        # match number (at least 3 digits) with or without alphanumeric following a dot, not in quotes
        qstat_command=None,
        qstat_findStatus=r'(?i)\s+[rqwecpd]{1,2}\s+',
        qdel_command=None,
    ):

        self.server = server
        if server is None:
            self.server = str(module_root['SETTINGS']['REMOTE_SETUP']['server'])
        self.tunnel = tunnel
        if tunnel is None:
            self.tunnel = str(module_root['SETTINGS']['REMOTE_SETUP']['tunnel'])
        self.remotedir = remotedir
        if remotedir is None:
            self.remotedir = str(module_root['SETTINGS']['REMOTE_SETUP']['workDir'])

        if isinstance(qsub_job, str):
            qsub_job = qsub_job.split('\n')
        qsub_job = [_f for _f in [x.strip() for x in qsub_job] if _f]
        try:
            ids = []
            for ii in range(-4, 0):  # check the last 4 lines in case the admins print messages like "bye... bye..."
                if len(qsub_job) >= abs(ii):
                    ids += [_f for _f in re.findall(qsub_findID, qsub_job[ii]) if _f]
            self.jobID = ids[-1]
        except IndexError:
            raise IndexError('Could not find a valid jobID in string `%s` with rule `%s`' % (qsub_job[-1], qsub_findID))
        if self.jobID.count('.') > 1:
            self.jobID = '.'.join(self.jobID.split('.')[:-1])
        printi('batch job ID: ' + self.jobID)

        self.qstat_command = qstat_command
        self.qstat_findStatus = qstat_findStatus
        self.qdel_command = qdel_command

    def identify_queuing_system(self):
        '''
        This function identifies qstat and qdel commands to be used, if these were not specified

        :return: None
        '''
        if self.qstat_command is None or self.qdel_command is None:
            sysinfo = remote_sysinfo(self.server, self.tunnel)

            if sysinfo['SQUEUE']:
                if self.qstat_command is None:
                    self.qstat_command = 'squeue'
                if self.qdel_command is None:
                    self.qdel_command = 'scancel'
            else:
                if self.qstat_command is None:
                    self.qstat_command = 'qstat'
                if self.qdel_command is None:
                    self.qdel_command = 'qdel'

    def qstat(self, quiet=True, sleep=0, std_out=None, std_err=None):
        '''
        `qstat` command (or equivalent)

        :param quiet: controls the output that is displayed to screen

            * False: prints the full output of the command

            * `select`: prints only the line involving the right jobID

            * True: nothing gets printed

        :param sleep: grace time in seconds before checking

        :return: the status of the job, if the jobID is found in the output of `qstat`. Otherwise None.
        '''
        if std_out is None:
            std_out = []
        if std_err is None:
            std_err = []
        std_out[:] = []
        std_err[:] = []
        self.identify_queuing_system()
        remote_execute(
            self.server,
            'sleep ' + str(sleep) + ';' + self.qstat_command,
            self.remotedir,
            self.tunnel,
            std_out=std_out,
            std_err=std_err,
            quiet=quiet,
            use_bang_command=False,
        )
        line = ''
        for line in std_out:
            if re.match(r'^\s*' + self.jobID + r'\s+.*', line):
                break
        if re.match(r'^\s*' + self.jobID + r'\s+.*', line):
            if quiet == 'select':
                printi(line)
            if len(re.findall(self.qstat_findStatus, line)):
                return re.findall(self.qstat_findStatus, line)[-1].strip()
            else:
                printi('Job %s has undefined/unrecognized status:\n%s' % (self.jobID, line))
        elif quiet is not False:
            printi('No job ' + self.jobID)

    def __call__(self):
        return self.qstat(quiet='select')

    def qdel(self, std_out=None, std_err=None):
        '''
        `qdel` command (or equivalent)
        '''
        if std_out is None:
            std_out = []
        if std_err is None:
            std_err = []
        std_out[:] = []
        std_err[:] = []
        self.identify_queuing_system()
        remote_execute(
            self.server,
            self.qdel_command + ' ' + str(self.jobID),
            self.remotedir,
            self.tunnel,
            std_out=std_out,
            std_err=std_err,
            use_bang_command=False,
        )

    def wait(self, timeout=None, sleep=10):
        """
        Wait for a job to finish

        :param timeout: Timeout in seconds after which the wait function will return

        :param sleep: Interval in seconds between checks

        :return: string with the last seen job status. If the job was not there, then a '?' is returned
        """
        t0 = time.time()
        last_status = '?'
        status = self.qstat(quiet=True, sleep=0, std_out=[], std_err=[])
        while True:
            if status is None:
                printi('Job ' + self.jobID + ' is not in the queue')
                break
            else:
                last_status = status
            if 'r' not in status.lower() and 'q' not in status.lower() and 'pd' not in status.lower():
                printi('Terminating job ' + self.jobID + ' wait with status: ' + status + ' (%3.1f' % (time.time() - t0) + ' sec)')
                break
            printi('Waiting job ' + self.jobID + ': ' + status + ' (%3.1f' % (time.time() - t0) + ' sec)')
            if timeout is not None and (time.time() - t0) > timeout:
                break
            status = self.qstat(quiet=True, sleep=sleep, std_out=[], std_err=[])
        return last_status

    def wait_print(self, output_file='', error_file='', progressFunction=None, extraButtons=None):
        """
        Wait for a job to finish and follow the output file and print the error file that the job generates

        :param output_file: output file that will be followed until the job ends (on the std_out)

        :param error_file: error file that will be printed when the job ends (on the std_err)

        :param progressFunction: user function to which the std-out of the process is passed and returns values from 0 to 100 to indicate progress towards completion

        :param extraButtons: dictionary with key/function that is used to add extra buttons to the GUI. The function receives a dictionary with the process std_out and pid
        """
        remote_upsync(
            self.server,
            os.sep.join([OMFITsrc, '..', 'bin', 'qprint']),
            self.remotedir,
            tunnel=self.tunnel,
            ignoreReturnCode=False,
            quiet=True,
        )
        if not len(output_file):
            output_file = '._no_output_file'
        command = './qprint ' + self.jobID + ' ' + output_file + ' ' + error_file
        if extraButtons is None:
            extraButtons = {}
        retcode = remote_execute(
            self.server,
            command,
            self.remotedir,
            self.tunnel,
            quiet=False,
            use_bang_command=False,
            progressFunction=progressFunction,
            extraButtons=extraButtons,
            ignoreReturnCode=True,
            forceRemote=True,
        )
        if retcode == 0:
            pass
        elif retcode == 9:
            raise OMFITexception('qprint stopped the queued job!')
        elif retcode == 10:
            raise ReturnCodeException('qprint could not detect the scheduler.')
        elif retcode == 255:
            raise OMFITexception('qprint detached from the job.')
        else:
            raise ReturnCodeException('qprint quit with return code {:}.'.format(retcode))

    def __str__(self):
        return 'job ' + self.jobID + ' on ' + self.server

    def __repr__(self):
        return self.__str__()


@_available_to_userTASK
def job_array(
    module_root, batch_lines, environment='', partition='', nproc_per_task=1, job_time='1', memory='2GB', batch_type='SLURM', **kw
):
    r"""
    Launch a (SLURM,PBS) job array

    :param module_root: The module instance from which servers, etc. are culled

    :param batch_lines: A multi-line string or list of strings that should be executed in parallel

    :param environment: A string to be executed to set up the environment before launching the batch job

    :param partition: A string to be inserted into the batch script that indicates
                      which partition(s) (comma separated) to run on; if None, execute batch_lines serially

    :param nproc_per_task: Number of processors to be used by each line of batch_lines

    :param job_time: Max wall time of each line of batch_lines - see sbatch --time option (default 1 minute)

    :param memory: Max memory usage of each cpu utilized by batch_lines - see sbatch --mem-per-cpu option (default 2GB)

    :param batch_type: Type of batch system (SLURM, PBS)

    :param \**kw: All other keywords are passed to OMFITx.executable

    :return: None
    """
    if partition == '':
        raise ValueError('Parition must be specified for job_array')
    inputs = kw.pop('inputs', [])

    batch_py = OMFITascii(
        'batch.py',
        fromString='''
import sys
import os
import shutil
args = sys.argv
input_table_fn = args[1]
ind = int(args[2])
with open(input_table_fn) as f:
    command = f.readlines()[ind]
idir = str(ind)
os.system(command)''',
    )
    if isinstance(batch_lines, (list, tuple)):
        batch_lines = '\n'.join(batch_lines)
    if not isinstance(batch_lines, str):
        raise TypeError('batch_lines should be a string or list')

    if batch_type == 'SLURM':
        batch_sh = OMFITascii(
            'batch.sh',
            fromString='''#!/bin/bash
#SBATCH -p {partition}
#SBATCH --ntasks={nproc_per_task}
#SBATCH --mem-per-cpu={memory}
#SBATCH --time={job_time}

#SBATCH --export=all

#SBATCH --output=arrayJob_%A_%a.out
#SBATCH --error=arrayJob_%A_%a.err
#SBATCH --array=0-{nsims}

PYTHON=`which python3||which python`
$PYTHON batch.py batch_lines $SLURM_ARRAY_TASK_ID
    '''.format(
                nsims=len(batch_lines.strip().split('\n')) - 1, **locals()
            ),
        )

        batch_lines = OMFITascii('batch_lines', fromString=batch_lines + '\n')
        inputs.extend([batch_py, batch_lines, batch_sh])
        execute_str = 'sbatch batch.sh'

    elif batch_type == 'PBS':
        batch_sh = OMFITascii(
            'batch.sh',
            fromString='''#!/bin/bash

#PBS -l walltime={job_time}
#PBS -l mem={memory}
#PBS -l ncpus={nproc_per_task}
#PBS -q {partition}

#PBS -o physics_job%A_%a.out
#PBS -e physics_job%A_%a.err
#PBS -t 1-{nsims}

cd $PBS_O_WORKDIR

python3 batch.py batch_lines $((PBS_ARRAYID-1))
    '''.format(
                nsims=len(batch_lines.strip().split('\n')), **locals()
            ),
        )

        batch_lines = OMFITascii('batch_lines', fromString=batch_lines + '\n')
        inputs.extend([batch_py, batch_lines, batch_sh])
        execute_str = 'qsub batch.sh'

    if environment:
        execute_str = '%s; %s' % (environment, execute_str)
    if 'executable' in kw:
        printe('executable passed to job_array is ignored')
        kw.pop('executable')
    kw.pop('queued', None)
    if partition:
        executable(module_root, inputs=inputs, executable=execute_str, queued=True, **kw)
    else:
        executable(module_root, inputs=inputs, executable='%s;%s' % (environment, batch_lines.read()), queued=False, **kw)


@_available_to_userTASK
def ide(
    module_root,
    ide,
    script=None,
    inputs=[],
    outputs=[],
    clean=True,
    interactive_input=None,
    server=None,
    tunnel=None,
    executable=None,
    workdir=None,
    remotedir=None,
    ignoreReturnCode=True,
    std_out=None,
    std_err=None,
    keepRelativeDirectoryStructure=True,
    arguments='',
):
    """
    High level function that simplifies local/remote execution of Integrated Development Environments (IDEs)

    This function will:
    1. cd to the local working directory
    2. Clear local/remote working directories
    3. Deploy the the "input" objects to local working directory
    4. Upload files them remotely
    5. Executes the IDE
    6. Download "output" files to local working directory

    The IDE executable, server and tunnel, and local and remote working directory depend on the MainSettings['SERVER'][ide]

    If the tunnel is an empty string, the connection to the remote server is direct. If server is an empty string, everything will occur locally and the remote working directory will be ignored.

    :param module_root: root of the module (e.g. `root`) or `OMFIT` itself

    :param ide: what IDE to execute (e.g. `idl` or `matlab`)

    :param inputs: list of input objects or path to files, which will be deployed in the local or remote working directory.
                   To deploy objects with a different name one can specify tuples (inputObject,'deployName')

    :param outputs: list o output files which will be fetched from the remote directory

    :param clean: clear local/remote working directories

        * "local": clean local working directory only

        * "local_force": force clean local working directory only

        * "remote": clean remote working directory only

        * "remote_force": force clean remote working directory only

        * True: clean both

        * "force": force clean both

        * False: clean neither

    :param arguments: arguments which will be passed to the executable

    :param interactive_input: interactive input to be passed to the executable

    :param server: override module server

    :param tunnel: override module tunnel

    :param executable: override module executable

    :param workdir: override module local working directory

    :param remotedir: override module remote working directory

    :param ignoreReturnCode: ignore return code of executable

    :param std_out: if a list is passed (e.g. []), the stdout of the program will be put there line by line

    :param std_err: if a list is passed (e.g. []), the stderr of the program will be put there line by line

    :param script: string with script to be executed. `script` option requires that `%s` in the command line location where you want the script filename to appear

    :return: return code of the command
    """

    if module_root is OMFIT:
        serverOptions = SERVER[ide]
        if ide not in serverOptions:
            raise OMFITexception(
                'Server `%s` does not have %s. Change/edit %s server accordingly.' % (SERVER(serverOptions['server']), ide, ide)
            )
    else:
        serverOptions = SERVER[module_root]
        if ide not in serverOptions:
            serverOptions = SERVER[ide]
            txt = 'Server `%s` does not have %s. Fallback on %s default `%s`' % (
                SERVER(SERVER[module_root]['server']),
                ide,
                ide,
                SERVER(serverOptions['server']),
            )
            if ide not in serverOptions:
                raise OMFITexception(
                    '\n' + txt + '\nServer `%s` does not have %s. Change/edit server accordingly.' % (SERVER(serverOptions['server']), ide)
                )
            else:
                printe(txt)

    if server is None:
        server = str(serverOptions['server'])
    if tunnel is None:
        tunnel = str(serverOptions['tunnel'])
    if executable is None:
        executable = str(serverOptions[ide])
        if ide == 'matlab':
            if script is None:
                executable += ' -nosplash'
            else:
                if isinstance(script, str):
                    script = (script, 'OMFIT_matlab_script.m')
                executable += """ -nosplash -nodesktop -r "try, run './%s'; catch exception, fprintf(2,getReport(exception));end;quit;" """
        else:
            if script is None:
                executable = "xterm -e '" + executable + "'"
            else:
                executable += ' "%s"'
    if remotedir is None or workdir is None:
        from omfit_classes.omfit_python import OMFITworkDir
    if remotedir is None:
        remotedir = OMFITworkDir(module_root, serverOptions['server'])
    if workdir is None:
        workdir = OMFITworkDir(module_root, '')
        if module_root is OMFIT:
            workdir = workdir.rstrip(os.sep) + os.sep + ide + os.sep

    return _executable(
        module_root,
        inputs=inputs,
        outputs=outputs,
        clean=clean,
        interactive_input=interactive_input,
        server=server,
        tunnel=tunnel,
        executable=executable,
        workdir=workdir,
        remotedir=remotedir,
        ignoreReturnCode=ignoreReturnCode,
        std_out=std_out,
        std_err=std_err,
        keepRelativeDirectoryStructure=keepRelativeDirectoryStructure,
        arguments=arguments,
        script=script,
    )


@_available_to_userTASK
class archive(object):
    def __init__(self, module_root, server=None, tunnel=None, remotedir=None, storedir=None, store_command=None, restore_command=None):
        '''
        High level function that simplifies archival of simulations files

        :param module_root: root of the module (e.g. `root`)

        :param server: override module `server`

        :param tunnel: override module `tunnel`

        :param storedir: directory where ZIP files are stored
            if storedir is None, then this will be sought under `module_root['SETTINGS']['REMOTE_SETUP']['storedir']`
            and finally under `SERVER[server]['storedir']`

        :param store_command: (optional) user-defined store command issued to store data (eg. for HPSS usage).
            Strings `{remotedir}` `{storedir}` and `{filename}` are substituted with actual `remotedir`, `storedir` and `filename`
            if `store_command` is `None`, then this will be sought under `module_root['SETTINGS']['REMOTE_SETUP']['store_command']`
            and finally under `SERVER[server]['store_command']`

        :param restore_command: (optional) user-defined restore command issued to restore data (eg. for HPSS usage).
            Strings `{remotedir}` `{storedir}` and `{filename}` are substituted with actual `remotedir`, `storedir` and `filename`
            if `restore_command` is `None`, then this will be sought under `module_root['SETTINGS']['REMOTE_SETUP']['restore_command']`
            and finally under `SERVER[server]['restore_command']`
        '''
        self.server = evalExpr(server)
        if server is None:
            self.server = evalExpr(module_root['SETTINGS']['REMOTE_SETUP']['server'])

        self.tunnel = evalExpr(tunnel)
        if tunnel is None:
            self.tunnel = evalExpr(module_root['SETTINGS']['REMOTE_SETUP']['tunnel'])

        self.storedir = evalExpr(storedir)
        if storedir is None and 'storedir' in module_root['SETTINGS']['REMOTE_SETUP']:
            self.storedir = evalExpr(module_root['SETTINGS']['REMOTE_SETUP']['storedir'])
        elif storedir is None and 'storedir' in SERVER[self.server]:
            self.storedir = evalExpr(SERVER[self.server]['storedir'])

        self.store_command = evalExpr(store_command)
        if store_command is None and 'store_command' in module_root['SETTINGS']['REMOTE_SETUP']:
            self.store_command = evalExpr(module_root['SETTINGS']['REMOTE_SETUP']['store_command'])
        elif store_command is None and 'store_command' in SERVER[self.server]:
            self.store_command = evalExpr(SERVER[self.server]['store_command'])

        self.restore_command = evalExpr(restore_command)
        if restore_command is None and 'restore_command' in module_root['SETTINGS']['REMOTE_SETUP']:
            self.restore_command = evalExpr(module_root['SETTINGS']['REMOTE_SETUP']['restore_command'])
        elif restore_command is None and 'restore_command' in SERVER[self.server]:
            self.restore_command = evalExpr(SERVER[self.server]['restore_command'])

        if self.storedir is None and (self.restore_command is None or self.restore_command is None):
            raise OMFITexception('server %s needs to have `storedir` or `store_command` and `restore_command` specified' % self.server)

    def store(self, remotedir, filename, quiet=False, background=False, force=False, store_command=None):
        '''
        Store `remotedir` to `filename` ZIP file

        :param remotedir: remote directory to archive (usually: `root['SETTINGS']['REMOTE_SETUP']['workdir']`)
            This parameter needs to be specified because the working directory can change.

        :param filename: filename to be used for archival

        :param quiet: print store process to screen

        :param background: put creation of ZIP archive in background (ignored if store_commnad is used)

        :param force: force store even if remotedir does not have `OMFIT` substring in it

        :param store_command: store command to be used

        :return: object instance
        '''
        if not force and not 'OMFIT' in str(remotedir):
            raise RuntimeError(
                'Refusing to store. This is a safety measure. The remote directory '
                + remotedir
                + ' does not contain the word "OMFIT" in it.\nAdd the word "OMFIT" as part of the path, or set force=True.'
            )

        if background is True:
            background = '&'
        else:
            background = ''

        self.filename = filename

        command = """(mkdir -p {storedir} && ls -a * | xargs zip -y -r {storedir}/{filename}) {background}""".format(
            storedir=self.storedir, filename=self.filename, background=background
        )

        if store_command is None and self.store_command is not None:
            store_command = self.store_command
        if store_command is not None:
            command = store_command.format(storedir=self.storedir, filename=self.filename, remotedir=remotedir)

        remote_execute(self.server, command, remotedir, self.tunnel, quiet=quiet, use_bang_command=False)

        return self

    def restore(self, remotedir, quiet=False, background=False, force=False, restore_command=None):
        '''
        Restore `filename` ZIP file to `remotedir`

        :param remotedir: remote directory to deflate to (usually: `root['SETTINGS']['REMOTE_SETUP']['workdir']`)
            This parameter needs to be specified because the working directory can change.

        :param quiet: print restore process to screen

        :param background: put restore of ZIP archive in background (ignored if restore_commnad is used)

        :param force: force restore even if remotedir does not have `OMFIT` substring in it

        :param restore_command: restore command to be used

        :return: object instance
        '''
        if not force and not 'OMFIT' in str(remotedir):
            raise RuntimeError(
                'Refusing to restore. This is a safety measure. The remote directory '
                + remotedir
                + ' does not contain the word "OMFIT" in it.\nAdd the word "OMFIT" as part of the path, or set force=True.'
            )

        if background is True:
            background = '&'
        else:
            background = ''

        command = """(unzip -o {storedir}/{filename}) {background}""".format(
            storedir=self.storedir, filename=self.filename, background=background
        )

        if restore_command is None and self.restore_command is not None:
            restore_command = self.restore_command
        if restore_command is not None:
            command = restore_command.format(storedir=self.storedir, filename=self.filename, remotedir=remotedir)

        remote_execute(self.server, command, remotedir, self.tunnel, quiet=quiet, use_bang_command=False)

        return self


@_available_to_userTASK
def glob(server='', file_filter='*', workDir='./', tunnel='', search_upstream=False):
    """
    Returns list of files in remote directory

    :params server: remote server

    :params file_filter: regular expression to filter files on (`*` by default)

    :params workdir: remote working directory

    :params tunnel: remote tunnel to use

    :params search_upstream: T/F: Search for the file in parent directories until it is found or / is reached.
    """
    std_out = []

    def glob1(glob_dir):
        remote_execute(
            server,
            r'\ls -1 -p -L ' + file_filter,
            glob_dir,
            tunnel,
            std_out=std_out,
            quiet=True,
            ignoreReturnCode=True,
            use_bang_command=False,
        )

        for k, line in enumerate(reversed(std_out[:-1])):
            if not len(line.strip()):
                break
        glob_files = [_f for _f in std_out[-k - 1 :] if _f]
        glob_files = [glob_dir.strip().rstrip(os.sep) + os.sep + x for x in glob_files]
        return glob_files

    if search_upstream:
        files = []
        dir2 = copy.copy(workDir)
        while not files and len(dir2) > len(os.sep):
            printd('  Search for {:} in {:}'.format(file_filter, dir2), topic='framework')
            files = glob1(dir2)
            dir2 = os.sep.join(dir2.split(os.sep)[0:-1])  # Strip another level of the path
    else:
        files = glob1(workDir)

    return files


@_available_to_userTASK
def email(to, subject, message, attachments=None, sysinfo=True, **kw):
    r"""
    Send an email

    :param to: must be one of
        1) a single address as a string
        2) a string of comma separated multiple address
        3) a list of string addresses

    :param subject: String

    :param message: String

    :param attachments: List of OMFITobjects or path to files

    :param sysinfo: Include system info at the bottom of the message

    :param \**kw: Extra arguments passed to the send_email utility function

    :return: string that user can decide to print to screen
    """
    fromm = kw.pop('fromm', OMFIT['MainSettings']['SETUP']['email'])

    files = []
    if attachments is not None:
        attachments = tolist(attachments)
        for item in attachments:
            if isinstance(item, str):
                files.append(item)
            elif isinstance(item, OMFITobject):
                item.save()
                files.append(item.filename)
            else:
                raise OMFITexception('email attachments can only be a list of OMFITobjects or path to files')

    if sysinfo:
        message += (
            '\n\n\n'
            f'OMFIT project: {str(OMFIT.filename)}\n'
            f'OMFIT directory: {OMFITsrc}\n'
            f'Git commit: {repo_str}\n'
            f'Python executable: {sys.executable}\n'
            f'Hostname: {" | ".join(platform.uname())}'
        )

    return send_email(fromm=fromm, to=to, subject=subject, message=message, attachments=files, **kw)


# ----------------------------
# f2py
# ----------------------------
def f2py(filename, modname):
    '''
    Run f2py on filename to get modname.so and return modname
    '''
    if f2py.f2py_exe is None:
        raise NotImplementedError('Could not find path to f2py')
    d, f = os.path.split(filename)
    cwd = os.getcwd()
    os.chdir(d)
    execute('rm -rf {1}.so*; {0} -c -m {1} {2} > compile_{1}.log; mv {1}*.so {1}.so'.format(f2py.f2py_exe, modname, f))
    os.chdir(cwd)
    load_dynamic(modname, '%s/%s.so' % (os.path.abspath(d), modname))


if not hasattr(f2py, 'f2py_exe'):
    ver_string = '.'.join(map(str, sys.version_info[:2]))
    if system_executable('f2py'):
        f2py.f2py_exe = system_executable('f2py')
    elif system_executable(f'f2py-{ver_string}'):
        f2py.f2py_exe = system_executable(f'f2py-{ver_string}')
    elif system_executable(f'f2py{ver_string}'):
        f2py.f2py_exe = system_executable(f'f2py{ver_string}')
    else:
        f2py.f2py_exe = None

# ----------------------------
# Synonyms for backward compatibility
# ----------------------------
OMFIT_backward_compatibility_mapper['OMFITx.titleGUI'] = 'OMFITx.TitleGUI'


def titleGUI(*args, **kw):
    return TitleGUI(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.lock'] = 'OMFITx.Lock'


def lock(*args, **kw):
    return Lock(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.Checkbutton'] = 'OMFITx.CheckBox'


def Checkbutton(*args, **kw):
    return CheckBox(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.CheckButton'] = 'OMFITx.CheckBox'


def CheckButton(*args, **kw):
    return CheckBox(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.compoundGUI'] = 'OMFITx.CompoundGUI'


def compoundGUI(*args, **kw):
    return CompoundGUI(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.closeGUI'] = 'OMFITx.CloseGUI'


def closeGUI(*args, **kw):
    return CloseGUI(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.closeAllGUIs'] = 'OMFITx.CloseAllGUIs'


def closeAllGUIs(*args, **kw):
    return CloseAllGUIs(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.updateGUI'] = 'OMFITx.UpdateGUI'


def updateGUI(*args, **kw):
    return UpdateGUI(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.end'] = 'OMFITx.End'


def end(*args, **kw):
    return End(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.mainSettings_ShotTimeDevice_GUI'] = 'OMFITx.ShotTimeDevice'


def mainSettings_ShotTimeDevice_GUI(*args, **kw):
    return ShotTimeDevice(*args, **kw)


OMFIT_backward_compatibility_mapper['OMFITx.AskUser'] = 'OMFITx.Dialog'


def AskUser(*args, **kw):
    return Dialog(*args, **kw)


# ---------------
# customize the GUI theme
# ---------------

ttk_styles = [
    'TButton',
    'TCheckbutton',
    'TCombobox',
    'TEntry',
    'TFrame',
    'TLabel',
    'TLabelFrame',
    'TMenubutton',
    'TNotebook',
    'TPanedwindow',
    'Horizontal.TProgressbar ',
    'Vertical.TProgressbar',
    'TRadiobutton',
    'Horizontal.TScale',
    'Vertical.TScale',
    'Horizontal.TScrollbar',
    'Vertical.TScrollbar',
    'TSeparator',
    'TSizegrip',
    'Treeview',
]

custom_ttk_styles = {}


def custom_ttk_style(type, **kw):
    '''
    Generates ttk styles dynamiecally and buffers them

    :param type: one of the ttk_styles

    :param kw: ttk style configuration attributes

    :return: dynamically generated ttk style name
    '''
    items = [x for x in kw.items() if isinstance(x[1], (int, str))]
    hash = omfit_hash(','.join([str(x[0]) + '=' + str(x[1]) for x in kw.items() if isinstance(x[1], (int, str))]), 10)
    style_name = 'style_%s.%s' % (hash, type)
    if style_name not in custom_ttk_styles:
        ttk.Style().configure(style_name, **dict(items))
        custom_ttk_styles[style_name] = dict(items)
    return style_name


_font_initialized = [False]


def update_gui_theme(location=None):
    """
    One place to set the ttk theme, reset custom styles, and update main gui elements.

    :return:
    """
    from utils_widgets import _defaultFont, OMFITfont

    _GUIappearance = OMFIT['MainSettings']['SETUP']['GUIappearance']
    ttk_style = ttk.Style()

    # update theme
    current_theme = ttk_style.theme_use()
    theme = _GUIappearance['theme']
    if not _font_initialized[0] or theme != ttk_style.theme_use():
        _font_initialized[0] = True
        if theme in ttk_style.theme_names():
            try:
                ttk_style.theme_use(theme)
            except Exception:
                printe('Theme not available for this installation...')
                printe('Valid themes are: {:}'.format(ttk_style.theme_names()))
                ttk_style.theme_use(current_theme)
        else:
            printe('Theme not available for this installation...')
            printe('Valid themes are: {:}'.format(ttk_style.theme_names()))
            ttk_style.theme_use(current_theme)

        # set default font to theme default
        f = tkFont.Font(font=ttk_style.lookup('TLabel', 'font'))
        _defaultFont.update(f.metrics())
        if theme != ttk_style.theme_use():
            try:  # MainSettings not defined soon enough for initial omfit_gui call
                OMFIT['MainSettings']['SETUP']['GUIappearance']['tree_rowheight_multiplier'] = 1.2
                OMFIT['MainSettings']['SETUP']['GUIappearance']['theme'] = ttk_style.theme_use()
                OMFIT['MainSettings']['SETUP']['GUIappearance']['GUI_font_family'] = _defaultFont['family']
                OMFIT['MainSettings']['SETUP']['GUIappearance']['GUI_font_size'] = _defaultFont['size']
            except Exception:
                printd('Unable to update MainSettings to match theme font')

    # make sure there are defaults (gets from system if not)
    OMFITfont()
    # change font for default styles
    ttk_style.configure('.', font=(_defaultFont['family'], _defaultFont['size'], _defaultFont['weight']))

    # OMFIT specific customization over styles

    # set the minimum width of a button
    ttk_style.configure('TButton', minwidth=4)
    # center labels by default
    ttk_style.configure('TLabel', anchor=tk.CENTER)
    # space Treeview correctly for the user's default font
    ttk_style.configure(
        'Treeview', rowheight=int(_defaultFont['linespace'] * OMFIT['MainSettings']['SETUP']['GUIappearance']['tree_rowheight_multiplier'])
    )
    # loop through all the ttk styles used in OMFIT and provide some alt styles
    for key in ttk_styles:
        # default styles
        ttk_style.configure(key, font=(_defaultFont['family'], _defaultFont['size'], _defaultFont['weight']))
        # custom styles
        ttk_style.configure('bold.' + key, font=(_defaultFont['family'], _defaultFont['size'], 'bold'))
        ttk_style.configure('small.' + key, font=(_defaultFont['family'], _defaultFont['size'] - 2, _defaultFont['weight']))
        ttk_style.configure(
            'flat.' + key, relief=tk.FLAT, width=1, font=(_defaultFont['family'], _defaultFont['size'], _defaultFont['weight'])
        )

        ttk_style.configure('important.' + key, font=(_defaultFont['family'], int(_defaultFont['size'] * 1.3), 'bold'))
        ttk_style.map('important.' + key, background=[('active', 'PaleGreen1')], foreground=[('active', 'lime green')])

        ttk_style.configure('dangerous.' + key, font=(_defaultFont['family'], _defaultFont['size'], 'normal', 'italic'))
        ttk_style.map('dangerous.' + key, background=[('active', 'salmon1')], foreground=[('active', 'firebrick2')])

        ttk_style.configure('commitment.' + key, font=(_defaultFont['family'], int(_defaultFont['size'] * 1.3), 'bold'))
        ttk_style.map('commitment.' + key, background=[('active', 'salmon1')], foreground=[('active', 'firebrick2')])

        ttk_style.configure(
            'flatwarning.' + key, font=(_defaultFont['family'], _defaultFont['size'], _defaultFont['weight']), relief=tk.FLAT
        )
        ttk_style.map('flatwarning.' + key, foreground=[('!invalid', 'orange')])

        ttk_style.configure('valid.' + key, fieldbackground='PaleGreen1')
        ttk_style.configure('check.' + key, fieldbackground='goldenrod1')
        ttk_style.configure('error.' + key, fieldbackground='salmon1')
        ttk_style.configure('exist.' + key, fieldbackground='azure3')

    # update elements explicitly set in OMFIT GUI
    # this function is initially called before treeGUI and GUI are set
    if OMFITaux.get('treeGUI', None) is not None:
        OMFITaux['treeGUI'].tags()  # updates tree view. Specifically, things with explicit fonts (dynamic italics, etc.)
    if OMFITaux.get('GUI', None) is not None:
        # update fonts
        OMFITaux['console'].configure(font=OMFITfont('normal'))  # Updates console
        OMFITaux['GUI'].browser_label_text.configure(font=OMFITfont('normal'))  # Updates browser entry
        OMFITaux['GUI'].namespaceComboBox.configure(font=OMFITfont('normal'))  # updates namespace drop-down
        for cb in OMFITaux['GUI'].command:  # update each commandbox tab
            cb.configure(font=OMFITfont(_defaultFont.get('weight2', ''), _defaultFont.get('size2', 0), 'Courier'))
        # update colors
        bg = ttk_style.lookup('TFrame', 'background')
        fbg = ttk_style.lookup('TEntry', 'fieldbackground')
        if not fbg:
            fbg = 'white'
        fg = ttk_style.lookup('TEntry', 'foreground')
        if not fg:  # robust to no specific color
            fg = 'black'
        OMFITaux['GUI'].menubar.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].filemenu.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].editmenu.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].plotmenu.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].figmenu.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].helpmenu.configure(background=bg, foreground=fg, font=OMFITfont())
        OMFITaux['GUI'].leftright_pan.configure(background=bg)
        OMFITaux['GUI'].updown_pan.configure(background=bg)
        OMFITaux['console'].configure(background=fbg, foreground=fg, highlightbackground=fbg)  # Updates console
        OMFITaux['GUI'].browser_label_text.configure(
            background=fbg, foreground=fg, highlightbackground=fbg, height=1
        )  # Updates browser entry
        for cb in OMFITaux['GUI'].command:
            cb.configure(background=fbg, foreground=fg, highlightbackground=fbg)

    return

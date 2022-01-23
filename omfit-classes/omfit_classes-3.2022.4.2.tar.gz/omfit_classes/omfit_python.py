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

from omfit_classes.omfit_base import _OMFITnoSave, all_pylab_imports, relativeLocations
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.utils_base import _streams, sleep
from omfit_classes import utils_base
from contextlib import contextmanager
import threading
import matplotlib
from matplotlib import pyplot
import numpy as np
import traceback

__all__ = [
    '_OMFITpython',
    'OMFITpythonTask',
    'OMFITpythonGUI',
    'OMFITpythonPlot',
    'OMFITpythonTest',
    'parallel_environment',
    'execGlobLoc',
    'defaultVars',
    'OMFITworkDir',
    'for_all_modules',
    'import_all_private',
    'import_mayavi',
    '_lock_OMFIT_preferences',
    'OMFITconsoleDict',
    'OMFITscriptsDict',
    'OMFITreloadedDict',
    'help',
    'omfit_pydocs',
    'threaded_logic',
]

# ------------------------------------
# Backward compatibility in modules scripts
# ------------------------------------
@deprecated
def xrange(*args, **kw):
    return range(*args, **kw)


@deprecated
def unichr(*args, **kw):
    return chr(*args, **kw)


# in python2 str and unicode were a subclass of basestring
basestring = str


class unicode(str):
    def __new__(cls, content):
        with warnings.catch_warnings():
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn("Initialization of deprecated class `{}`".format(cls.__name__), category=DeprecationWarning)
        return str.__new__(cls, content.upper())


# ------------------------------------
# Namespaces
# ------------------------------------
class OMFITnamespace(dict, _OMFITnoSave):
    """
    Same class of dict, but is not saved when a project is saved
    This class is used to handle namespaces, which should not alter the ._OMFITparent, ._OMFITkeyName of objects which are used within of the namespace
    """

    pass


OMFITconsoleDict = OMFITnamespace()  # console namespace
OMFITscriptsDict = OMFITnamespace()  # last script execution namespace
OMFITreloadedDict = OMFITnamespace()

# ------------------------------------
# Script execution within the OMFIT world
# ------------------------------------
global ExecDiagPtr


def _lock_OMFIT_preferences(f):
    def f_locked(*args, **kw):
        # backup matplotlib.rcparams
        backend_backup = matplotlib.get_backend()
        cBackup = {}
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            cBackup.update(copy.deepcopy(list(matplotlib.rcParams.items())))

        # apply user plot customizations
        if 'PlotAppearance' in OMFIT['MainSettings']['SETUP']:
            for key in OMFIT['MainSettings']['SETUP']['PlotAppearance']:
                try:
                    if key in ['startup_style']:
                        pass
                    elif key in ['lines.cmap']:
                        if OMFIT['MainSettings']['SETUP']['PlotAppearance'][key][0] == 'blind':
                            pyplot.rc('axes', prop_cycle=default_colorblind_line_cycle)
                        else:
                            cycle_cmap(
                                OMFIT['MainSettings']['SETUP']['PlotAppearance'][key][1],
                                cmap=OMFIT['MainSettings']['SETUP']['PlotAppearance'][key][0],
                            )
                    else:
                        matplotlib.rcParams[key] = OMFIT['MainSettings']['SETUP']['PlotAppearance'][key]
                except Exception as _excp:
                    printw("OMFIT['MainSettings']['SETUP']['PlotAppearance'][%s] has issues: %s" % (key, repr(_excp)))

        # backup np numerical exceptions
        npBackp = np.seterr(all='warn')

        try:
            # context manager for warnings
            with warnings.catch_warnings():
                return f(*args, **kw)

        finally:
            pyplot.ion()
            # restore np numerical exceptions
            np.seterr(**npBackp)
            # restore matplotlib.rcparams
            if backend_backup != matplotlib.get_backend():
                pyplot.switch_backend(backend_backup)
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                for key in cBackup:
                    try:
                        matplotlib.rcParams[key] = cBackup[key]
                    except Exception:
                        pass  # some may fail? `dvipnghack` does

    return f_locked


@_lock_OMFIT_preferences
def execGlobLoc(obj, userDict, inputDict, persistentDict, runDict, prerun='', postrun=''):
    """
    This fucntion is used to execute python strings or OMFITpython objects

    The `defaultVars` function sets the variables defaults in the running script
    Note that use of this function will enforce that all the variables that are
    passed to the script are defaulted to some value using this function.

    :param obj: _OMFITpython object to be executed

    :param userDict: dictionary containing variables passed by the user to be placed in the namespace

    :param inputDict: dictionary containing variables to be placed in the namespace

    :param persistentDict: dictionary containing variables to be placed in the namespace.
                           This dictionary will be updated with the resulting variables
                           and will be returned e.g. OMFITconsoleDict

    :param runDict: This dictionary will be updated with the resulting variables.
                    e.g. OMFITscriptsDict

    :param prerun: string which is prepended to the object to be run

    :param postrun: string which is appended to the object to be run

    :return: updated persistentDict
    """

    # execute string or _OMFITpython objects
    if isinstance(obj, str):
        filename = '<string>'
        execString = obj
    elif isinstance(obj, _OMFITpython):
        filename = obj.filename
        with open(filename, 'r') as _f:
            execString = _f.read()
    else:
        raise OMFITexception('execGlobLoc can execute either <strings> or OMFITpython objects')

    # move some special keywords away from the userDict
    for k in [
        'compoundGUI',
        'noGUI',
        'defaultVarsGUI',
        'headerGUI',
        'footerGUI',
        'nprocs',
        'process_id',
        'nsteps',
        'step_id',
        'IDE',
        'step_name',
    ]:
        if k in userDict:
            inputDict[k] = userDict[k]
            del userDict[k]
        elif k in ['process_id', 'step_id']:
            inputDict[k] = 0
        elif k in ['step_name']:
            inputDict[k] = '0'
        elif k in ['nprocs', 'nsteps']:
            inputDict[k] = 1
        else:
            inputDict[k] = None
    inputDict['is_prun'] = bool(len(OMFITaux['prun_process']))

    # IDE interface
    inputDict['IDE'] = SERVER

    # define execution namespace
    GlobLoc = {}
    GlobLoc['GlobLoc'] = GlobLoc
    GlobLoc.update(all_pylab_imports)
    GlobLoc.update(globals())
    GlobLoc.update(inputDict)
    GlobLoc.update(userDict)
    GlobLoc.update(persistentDict)
    runDict.clear()

    def get_OMFITlib_module(fullname):
        if 'root' not in GlobLoc or 'LIB' not in GlobLoc['root'] or fullname not in GlobLoc['root']['LIB']:
            raise ImportError(fullname)
        elif not fullname.startswith('OMFITlib_'):
            raise OMFITexception("OMFIT module library files should be in root['LIB']['OMFITlib_...']")

        if isinstance(GlobLoc['root']['LIB'][fullname], OMFITpythonTask):
            filename = GlobLoc['root']['LIB'][fullname].filename

            class OMFITmodule_lib(object):
                pass

            mod = OMFITmodule_lib()
            mod.__dict__.update(GlobLoc)
            if '__all__' in mod.__dict__:
                del mod.__dict__['__all__']
            with open(filename) as _f:
                exec_string = _f.read()
            exec(compile(exec_string, filename, 'exec'), mod.__dict__)
            for item in list(mod.__dict__.keys()):
                if (
                    item not in GlobLoc
                    and inspect.isclass(mod.__dict__[item])
                    and issubclass(mod.__dict__[item], (OMFITobject, SortedDict))
                ):
                    printe(
                        '%s is being removed from the namespace: classes inheriting from OMFITobject or SortedDict are not supported in OMFITlib_ files'
                        % item
                    )
                    del mod.__dict__[item]
            return mod

    import importlib.abc
    import importlib.machinery

    class OMFITimporter(importlib.abc.Loader):
        def create_module(self, spec):
            fullname = spec.name
            return get_OMFITlib_module(fullname)

        def exec_module(self, module):
            pass

    class DependencyInjectorFinder(importlib.abc.MetaPathFinder):
        def __init__(self, loader):
            self._loader = loader

        def find_spec(self, fullname, path, target=None):
            if (
                'root' in GlobLoc
                and 'LIB' in GlobLoc['root']
                and fullname in GlobLoc['root']['LIB']
                and isinstance(GlobLoc['root']['LIB'][fullname], OMFITpythonTask)
            ):
                return importlib.machinery.ModuleSpec(fullname, self._loader)
            elif fullname.startswith('OMFITlib_'):
                raise OMFITexception("OMFIT module library files should be in root['LIB']['OMFITlib_...']")
            return None

    # import hook to sys.meta_path
    this_importer = DependencyInjectorFinder(OMFITimporter())
    sys.meta_path.insert(0, this_importer)

    # define defaultVars
    if isinstance(obj, OMFITpythonPlot):

        def defaultVars(**varDict):
            fig = varDict.pop('fig', None)
            if fig is None:
                fig = pyplot.gcf()
            userDict['fig'] = varDict['fig'] = fig
            return _defaultVars(userDict, inputDict, GlobLoc, **varDict)

    else:

        def defaultVars(**varDict):
            return _defaultVars(userDict, inputDict, GlobLoc, **varDict)

    GlobLoc['defaultVars'] = defaultVars

    # override input
    def input(*args, **kw):
        raise Exception('OMFIT scripts do not support input()')

    GlobLoc['input'] = input

    GlobLoc['__file__'] = filename

    # set default debug topic based on module name
    def _printd(*args, **kw):
        kw.setdefault('topic', GlobLoc['rootName'])
        return printd(*args, **kw)

    _printd.__doc__ = printd.__doc__
    GlobLoc['printd'] = _printd

    # define environment that enables dynamic switching of execution namespace
    @contextmanager
    def namespace_environment(location):
        """
        This environment allows execution of code
        as if the code was at the location specified
        by the user

        :param location: OMFIT tree location

        :return: tree location namespace
        """
        if isinstance(location, str):
            location = eval(location)
        loc = relativeLocations(location)
        bkp_namespace = {}
        for item in loc:
            if item in GlobLoc:
                bkp_namespace[item] = GlobLoc[item]
        GlobLoc.update(loc)
        try:
            yield loc

        finally:
            for item in loc:
                if item in bkp_namespace:
                    GlobLoc[item] = bkp_namespace[item]
                else:
                    del GlobLoc[item]

    GlobLoc['namespace_environment'] = namespace_environment

    # execution diagram
    import time

    if isinstance(obj, (OMFITpythonTask, OMFITpythonPlot)):
        global ExecDiagPtr
        if ExecDiagPtr is ExecDiag:
            del ExecDiag[:]
        ExecDiagPtrOld = ExecDiagPtr
        ExecDiagPtr = []
        ExecDiagPtrOld.append({'filename': filename, 'time': time.time(), 'memory': memuse(as_bytes=True), 'child': ExecDiagPtr})

    # execute
    try:
        if len(prerun):
            exec(compile(prerun, 'prerun', "exec"), GlobLoc)

        try:
            exec(compile(execString, filename, "exec"), GlobLoc)
        finally:
            if len(postrun):
                exec(compile(postrun, 'postrun', "exec"), GlobLoc)

        # return whole execution
        return GlobLoc

    except EndOMFITpython:
        return GlobLoc

    finally:
        # find what variables were actually defined within the script
        for k in list(GlobLoc.keys()):
            if k in ['defaultVars', 'input', 'GlobLoc', 'namespace_environment'] and k in GlobLoc and GlobLoc[k] is eval(k):
                continue
            elif k in ['printd'] and GlobLoc[k] is eval('_' + k):
                continue
            elif k in ['ExecDiagPtr']:
                continue
            elif k in list(OMFITreloadedDict.keys()):
                del OMFITreloadedDict[k]
            elif not (
                (k in all_pylab_imports and id(GlobLoc[k]) == id(all_pylab_imports[k]))
                or (k in globals() and id(GlobLoc[k]) == id(globals()[k]))
                or (k in inputDict and id(GlobLoc[k]) == id(inputDict[k]))
                or (k in userDict and id(GlobLoc[k]) == id(userDict[k]))
            ):
                persistentDict[k] = GlobLoc[k]
        runDict.update(persistentDict)

        # remove OMFITlib_ imports from sys.module cache and restore original import system
        if this_importer in sys.meta_path:
            for item in list(sys.modules.keys()):
                if item.startswith('OMFITlib_'):
                    del sys.modules[item]
            sys.meta_path.remove(this_importer)

        # update last seen activity
        OMFITaux['lastActivity'] = time.time()

        # update execution diagram
        if isinstance(obj, OMFITpythonTask):
            if len(ExecDiagPtrOld):
                ExecDiagPtrOld[-1]['time'] = time.time() - ExecDiagPtrOld[-1]['time']
                memory = memuse(as_bytes=True)
                if memory > 0:
                    ExecDiagPtrOld[-1]['memory'] = memory - ExecDiagPtrOld[-1]['memory']
                else:
                    ExecDiagPtrOld[-1]['memory'] = 'N/A'
            ExecDiagPtr = ExecDiagPtrOld


def defaultVars(**kw):
    r"""
    Function used to setup default variables in an OMFIT script (of type
    OMFITpythonTask, OMFITpythonTest, OMFITpythonGUI, or OMFITpythonPlot)
    Really the magic function that allows OMFIT scripts to act as a function

    :param \**kw: keyword parameter dictionary with default value

    :return: dictionary with variables passed by the user

    To be used as
    dfv = defaultVars(var1_i_want_to_define=None, var2_i_want_to_define=None)
    and then later in the script, one can use var1_i_want_to_define or var2_i_want_to_define

    Implications of python passing variables by reference are noted in
    https://medium.com/@meghamohan/mutable-and-immutable-side-of-python-c2145cf72747
    """


def _defaultVars(_userDict, _inputDict, _GlobLoc, **varDict):
    """
    :param userDict: dictionary containing variables passed by the user to be placed in the namespace

    :param inputDict: dictionary containing variables to be placed in the namespace

    :param _GlobLoc: execution dictionary to be updated

    :param varDict: variables accepted by defaultVars

    :return: dictioinary with variables used
    """
    # passsing `strict_defaultVars=False` disables check of what user passes to the script
    strict_defaultVars = _userDict.pop('strict_defaultVars', True)
    # setting `strict_defaultVars=False` in defaultVars disables check of what user passes to the script
    strict_defaultVars = varDict.pop('strict_defaultVars', strict_defaultVars)

    if len(set(_userDict.keys()).difference(set(varDict.keys()))):
        var = set(_userDict.keys()).difference(set(varDict.keys()))
        txt = 'Unexpected argument `%s` passed to OMFIT script.\nSupported defaultVars are `%s`.' % (
            ', '.join(var),
            ', '.join(varDict.keys()),
        )
        if strict_defaultVars:
            raise ValueError(txt)
        else:
            printw(txt)
    if len(set(_userDict.keys()).intersection(set(_inputDict.keys()))):
        var = set(_userDict.keys()).intersection(set(_inputDict.keys()))
        printw('Reserved argument passed to OMFIT script: ' + ','.join(var))
    if len(set(varDict.keys()).intersection(set(_inputDict.keys()))):
        var = set(varDict.keys()).intersection(set(_inputDict.keys()))
        printw('Reserved argument to defaultVars: ' + ','.join(var))

    # display GUI for setting defaultVars
    if _inputDict['defaultVarsGUI']:

        for var in list(_userDict.keys()):
            varDict[var] = _userDict[var]

        finished = tk.BooleanVar()
        finished.set(False)
        aborted = tk.BooleanVar()
        aborted.set(False)

        def _repr(location):
            if isinstance(location, np.ndarray) and len(location.shape) == 1:
                return repr(np.atleast_1d(location).tolist())
            else:
                return repr(location)

        def _Entry(parent, data, object=False):
            value = tk.StringVar()
            valueOrig = tk.StringVar()
            e = ttk.Entry(parent, textvariable=value, width=50)
            e.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

            valueOrig.set(_repr(data))
            value.set(_repr(data))

            if object:
                # remove quotes
                for v in [value, valueOrig]:
                    f = v.get()[0]
                    l = v.get()[-1]
                    if f == l and f in ['"', "'"]:
                        v.set(v.get()[1:-1])

            def update_value():
                if object:
                    try:
                        tmp = eval(value.get())
                        valueOrig.set(value.get())
                    except Exception as _excp:
                        if value.get().endswith('from memory>'):
                            valueOrig.set(value.get())
                        pass
                else:
                    tmp = eval(value.get())
                    data = eval(valueOrig.get())
                    if isinstance(tmp, list) and isinstance(data, np.ndarray) and len(data.shape) == 1:
                        tmp = np.atleast_1d(tmp)
                    valueOrig.set(_repr(tmp))
                checkKeyPressed()

            e.bind(sequence="<Return>", func=lambda event=None: update_value())
            e.bind(sequence="<KP_Enter>", func=lambda event=None: update_value())

            def checkKeyPressed(event=None):
                try:
                    try:
                        if object:
                            eval(value.get()) == eval(valueOrig.get())
                        else:
                            _repr(eval(value.get())) == _repr(eval(valueOrig.get()))
                        e.config(background='white')
                    except Exception as _excp:
                        if object and value.get().endswith('from memory>'):
                            e.config(background='white')
                        else:
                            e.config(background='salmon1')
                except Exception:
                    pass

            e.bind(sequence="<Key>", func=lambda event=None: e.after(1, checkKeyPressed))

            def escape(event=None):
                value.set(valueOrig.get())
                checkKeyPressed()

            e.bind(sequence="<Escape>", func=lambda event=None: e.after(1, escape))

            return value

        def onReturn(event=None):
            for var in list(varDict.keys()):
                if var in value:
                    if var in objDict and value[var].get() == '<%s from memory>' % varDict[var].__class__.__name__:
                        _userDict[var] = varDict[var]
                    else:
                        _userDict[var] = eval(value[var].get())
            top.update_idletasks()
            finished.set(True)
            top.update_idletasks()

        def onEscape(event=None):
            top.update_idletasks()
            finished.set(True)
            top.update_idletasks()

        def onAbort(event=None):
            top.update_idletasks()
            aborted.set(True)
            finished.set(True)
            top.update_idletasks()

        if len(OMFITaux['pythonRunWindows']) and OMFITaux['pythonRunWindows'][-1] is not None:
            top = ttk.Frame(OMFITaux['pythonRunWindows'][-1])
            top.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH)
        else:
            top = tk.Toplevel(OMFITaux['rootGUI'])
            top.transient(OMFITaux['rootGUI'])
            top.protocol("WM_DELETE_WINDOW", 'break')

        value = {}
        objDict = {}
        for var in sorted(list(varDict.keys()), key=lambda x: str(x).lower()):
            frm = ttk.Frame(top)
            ttk.Label(frm, text=var + ' = ').pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            try:
                if isinstance(varDict[var], OMFITtypes) or isinstance(varDict[var], OMFITtree):
                    objDict[var] = treeLocation(varDict[var])[-1]
                    if objDict[var] == '':
                        objDict[var] = '<%s from memory>' % varDict[var].__class__.__name__
                    value[var] = _Entry(frm, objDict[var], object=True)
                elif _repr(eval(_repr(varDict[var]))) == _repr(varDict[var]):
                    value[var] = _Entry(frm, varDict[var])
                else:
                    raise
            except Exception:
                cls = ''
                if hasattr(varDict[var], '__class__'):
                    cls = '<' + varDict[var].__class__.__name__ + '> '
                ttk.Label(frm, text=cls + 'object not editable in GUI').pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE)
            frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx=5)
        frm = ttk.Frame(top)
        ttk.Button(frm, text='Continue >>', command=onReturn).pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        ttk.Button(frm, text='Abort', command=onAbort).pack(side=tk.LEFT, expand=tk.NO)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        top.bind("<Escape>", onEscape)
        top.update_idletasks()
        top.wait_variable(finished)
        top.destroy()

    if _inputDict['defaultVarsGUI'] and aborted.get():
        raise EndAllOMFITpython('Aborted by user in defaultVars')

    for var in list(varDict.keys()):
        if var not in _userDict:
            if var.startswith('**'):
                varDict.update(varDict[var])
                _userDict.update(varDict[var])
                if var in _userDict:
                    del _userDict[var]
                if var in varDict:
                    del varDict[var]
            else:
                _userDict[var] = varDict[var]
        else:
            if var.startswith('**'):
                _userDict.update(_userDict[var])
                varDict.update(_userDict[var])
                if var in _userDict:
                    del _userDict[var]
                if var in varDict:
                    del varDict[var]
            else:
                varDict[var] = _userDict[var]

    _GlobLoc.update(_userDict)

    return varDict


ExecDiag = []
global ExecDiagPtr
ExecDiagPtr = ExecDiag


def OMFITworkDir(root=None, server=''):
    """
    This is a convenience function which returns the string for the working directory of OMFIT modules (remote or local).
    The returned directory string is compatible with parallel running of modules. The format used is:
    [server_OMFIT_working_directory]/[projectID]/[mainsettings_runID]/[module_tree_location]-[module_runid]/[p_multiprocessing_folder]/

    :param root: root of the module (or string)

    :param server: remote server. If empty string or None, then the local working directory is returned.

    :return: directory string
    """

    # speedup: evaluate expressions
    server = evalExpr(server)

    dir = ''

    if server:
        server0, server = SERVER.handleServer(server)

    # local or remote
    if not server or server not in OMFIT['MainSettings']['SERVER']:
        dir = OMFIT['MainSettings']['SETUP']['workDir'].rstrip(os.sep) + os.sep
        # local does not need project name, since every OMFIT
        # instance already works in its own unique directory

    else:
        dir = SERVER[server]['workDir'].rstrip(os.sep) + os.sep

        # projectID
        if 'projectID' in OMFIT['MainSettings']['EXPERIMENT'] and OMFIT['MainSettings']['EXPERIMENT']['projectID'] != None:
            dir += OMFIT['MainSettings']['EXPERIMENT']['projectID'] + os.sep

        elif OMFIT.filename:
            tmp = re.sub(os.sep + r'OMFITsave\.txt$', '', OMFIT.filename)
            tmp = re.sub(r'\.zip$', '', tmp)
            tmp = os.path.split(tmp)[-1]
            dir += tmp + os.sep

    # project runid (ok, even without a project name)
    if OMFIT['MainSettings']['EXPERIMENT']['runid'] != None:
        dir += str(OMFIT['MainSettings']['EXPERIMENT']['runid']) + os.sep

    # tree location across modules with runid
    if isinstance(root, str):
        dir += root.strip(os.sep) + os.sep
    elif root is not OMFIT:
        locations = relativeLocations(root, dependencies=False)
        tmp = []
        for k in range(1, len(locations['OMFITmodulesName'])):
            modName = parseLocation(locations['OMFITmodulesName'][k])[-1].replace(" ", "")
            runid = ''
            if locations['OMFITmodules'][k]['SETTINGS']['EXPERIMENT']['runid'] != None:
                runid = '-' + str(locations['OMFITmodules'][k]['SETTINGS']['EXPERIMENT']['runid'])
            tmp.append(modName + runid)
        dir += '__'.join(tmp) + os.sep

    # parallelism
    if not len(OMFITaux['prun_process']):
        dir += 'p0' + os.sep
    else:
        dir += 'p' + '_'.join(map(str, OMFITaux['prun_process'])) + os.sep

    return dir


def for_all_modules(doThis='', deploy=False, skip=False, these_modules_only=None):
    """
    This is a utility function (to be used by module developers) which can be used to execute the same command on all of the modules
    Note that this script will overwrite the content of your OMFIT tree.

    :param doThis: python script to execute.
       In this script the following variables are defined
       ``root`` contains the reference to the current module being processed,
       ``moduleID`` the moduleID,
       ``rootName`` the location of the module in the tree
       ``moduleFile`` the module filename

    :param deploy: save the modules back on their original location

    :param skip: skip modules that are already in the tree

    :param these_modules_only: list of modules ID to process (useful for development of `doThis`)

    :return: None
    """
    moduleList = OMFIT.availableModules(quiet=True)

    if these_modules_only is None:
        these_modules_only = sorted(list(moduleList.keys()), key=lambda x: x.lower())
    else:
        these_modules_only = [moduleFile for moduleFile in moduleList if moduleList[moduleFile]['ID'] in these_modules_only]

    for moduleFile in these_modules_only:
        printi('--== PROCESSING: ' + moduleFile + ' ==--')

        moduleID = moduleList[moduleFile]['ID']
        rootName = "OMFIT['%s']" % moduleID

        if not skip or moduleID not in OMFIT:

            OMFIT.loadModule(
                moduleList[moduleFile]['path'], location=rootName, withSubmodules=False, availableModulesList=moduleList, checkLicense=False
            )

            root = eval(rootName)

            exec(doThis, globals(), locals())

            if deploy:
                printi('Deploying to:' + moduleList[moduleFile]['path'])
                module.deploy_module(moduleList[moduleFile]['path'], zip=False)


def import_all_private(module_str):
    """
    This function is used to import all private attributes from a module
    Can be used in a script like this::

    >> locals().update(import_all_private('omfit_classes.OMFITx'))
    """
    for _item in dir(eval(module_str)):
        exec('from %s import %s' % (module_str, _item), globals(), locals())
    return locals()


def import_mayavi(verbose=True):
    """
    This function attempts to import mayavi, mayavi.mlab
    while avoiding known institutional installation pitfalls
    as well as known tk vs qt backend issues.

    :param verbose: bool. Prints a warning message if mayavi can't be imported
    :return: obj. mayavi if it was successfully imported, None if not
    """
    mayavi = None
    _streams.backup()
    try:
        if is_localhost(['ltserv', 'abacus', 'ukstar']):
            raise ImportError("IPPCZ, NFIR mayavi - vtk have consistency conflicts")
        with parallel_environment():
            import mayavi, mayavi.mlab
    except Exception as _excp:
        if verbose:
            printw("WARNING: The 3D plotting module 'mayavi' is not supported by this python distribution")
    finally:
        _streams.restore()
    return mayavi


# ---------------------
# OMFIT pythons
# ---------------------
class _OMFITpython(OMFITascii):
    """Python script"""

    _header = '''"""
This script <fill in purpose>

defaultVars parameters
----------------------
:param kw1: kw1 can be passed to this script as <path to script>.run(kw1='hello')
"""

defaultVars(kw1=None)

print(kw1)
'''

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        if not os.stat(self.filename).st_size:
            with open(self.filename, 'w') as f:
                f.write("#-*-Python-*-\n# Created by " + os.environ['USER'] + " at " + utils_base.now() + "\n\n")
                if 'OMFITlib_' not in os.path.split(filename)[1]:
                    f.write(self._header)
        if (
            'MainSettings' in OMFIT
            and 'SETUP' in OMFIT['MainSettings']
            and OMFIT['MainSettings']['SETUP'].get('format_python_on_load', False)
        ):
            self.format()
        self._done_tidy = False

    def _create_backup_copy(self):
        """
        Hard-link script to backup scripts folder
        """

        if not os.path.exists(OMFITscriptsBackupDir):
            os.makedirs(OMFITscriptsBackupDir)
        hashed_filename = (
            OMFITscriptsBackupDir
            + os.sep
            + os.path.splitext(os.path.split(self.filename)[1])[0]
            + '__'
            + str(omfit_hash(self.filename, 10))
            + '.py'
        )
        if os.path.exists(hashed_filename):
            os.remove(hashed_filename)

        try:
            os.link(self.filename, hashed_filename)
            printd('Created script backup copy of `%s` to `%s`' % (self.filename, hashed_filename), topic='backup_scripts')
        except OSError as _excp:
            warnings.warn('OMFIT is unable to create script backup copies')
            printd(
                'Unable to produce script backup copy of `%s` to `%s`: %s' % (self.filename, hashed_filename, repr(_excp)),
                topic='backup_scripts',
            )
            hashed_filename = None

        # cleanup: keep only the most recent n backedup files
        n = 1000
        files = [f for f in glob.glob(OMFITscriptsBackupDir + "/*") if os.path.exists(f)]
        files.sort(key=lambda x: os.path.getmtime(x))
        files = list(reversed(files))
        for k in reversed(list(range(n, len(files)))):
            printd('Backup file %s has been removed' % files[k], topic='backup_scripts')
            os.remove(files[k])
        return hashed_filename

    def _tidy(self, force=False):
        """
        Perform Python code cleanup
        """
        if force or not hasattr(self, '_done_tidy') or not self._done_tidy:
            printd('called tidy on ' + self.filename, topic='framework')
            with open(self.filename, 'r') as fh:
                s = fh.read()
            new_s = []
            for si in s.splitlines():
                new_s.append(si.rstrip())
            new_s = '\n'.join(new_s).rstrip() + '\n'

            for old_name, new_name in list(OMFIT_backward_compatibility_mapper.items()):
                new_s = new_s.replace(old_name, new_name)

            if new_s != s:
                with open(self.filename, 'w') as fh:
                    fh.write(new_s)
            self._done_tidy = True
            if (
                'MainSettings' in OMFIT
                and 'SETUP' in OMFIT['MainSettings']
                and OMFIT['MainSettings']['SETUP'].get('format_python_on_load', False)
            ):
                self.format()

    def format(self, verbose=False):
        """
        Apply OMFIT file formatting standard

        :param verbose: print if python script is formatted
        """
        tmp = omfit_file_formatter(self.filename, overwrite=True)
        if verbose:
            if tmp is False:
                printi(os.path.basename(self.filename) + ' was already properly formatted')
            elif tmp is None:
                printw(os.path.basename(self.filename) + ' was not formatted to avoid GitHub conflicts')
            else:
                printi(os.path.basename(self.filename) + ' is now formatted')

    def __run__(self, _relLoc=None, _OMFITscriptsDict=True, _OMFITconsoleDict=False, prerun='', postrun='', **kw):
        oldDir = os.getcwd()

        if _relLoc is None:
            _relLoc = relativeLocations(self)

        # change working directory to the module
        if (
            'root' in _relLoc
            and 'SETTINGS' in _relLoc['root']
            and 'SETUP' in _relLoc['root']['SETTINGS']
            and 'workDir' in _relLoc['root']['SETTINGS']['SETUP']
        ):
            workdir = str(_relLoc['root']['SETTINGS']['SETUP']['workDir'])
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            os.chdir(workdir)

        lastRunModule_bkp = OMFITaux['lastRunModule']
        if 'rootName' in _relLoc:
            OMFITaux['lastRunModule'] = _relLoc['rootName']

        try:
            if _OMFITscriptsDict:
                tmp = execGlobLoc(
                    self, userDict=kw, inputDict=_relLoc, persistentDict={}, runDict=OMFITscriptsDict, prerun=prerun, postrun=postrun
                )
            elif _OMFITconsoleDict:
                tmp = execGlobLoc(
                    self, userDict=kw, inputDict=_relLoc, persistentDict=OMFITconsoleDict, runDict={}, prerun=prerun, postrun=postrun
                )
            else:
                tmp = execGlobLoc(self, userDict=kw, inputDict=_relLoc, persistentDict={}, runDict={}, prerun=prerun, postrun=postrun)
            OMFITaux['lastRunModule'] = lastRunModule_bkp
            return tmp

        except EndOMFITpython:
            pass

        finally:
            os.chdir(oldDir)


_update_alarm = []


class OMFITpythonTask(_OMFITpython):
    """Python script for OMFIT tasks"""

    def __init__(self, filename, **kw):
        _OMFITpython.__init__(self, filename, **kw)

    def __call__(self, **kw):
        return self.run(**kw)

    def _startGUI(self, **kw):
        kw.setdefault('noGUI', False)
        if OMFITaux['rootGUI'] is None:
            kw['noGUI'] = True

        if len(OMFITaux['pythonRunWindows']):
            IcreatedIt = False
        else:
            IcreatedIt = time.time()

            OMFITaux['haltWindow'] = None
            if not OMFIT_is_in_debug_mode and OMFITaux['rootGUI'] is not None and OMFIT['MainSettings']['SETUP']['show_halt_window']:
                OMFITaux['haltWindow'] = subprocess.Popen(
                    [sys.executable, OMFITsrc + '/omfit_halt.py', str(os.getpid()), re.sub("#", r"\#", OMFITaux['session_color'])]
                ).pid

            if kw['noGUI']:
                OMFITaux['pythonRunWindows'] = [None]
            else:
                OMFITaux['pythonRunWindows'] = [tk.Toplevel()]
                OMFITaux['pythonRunWindows'][0].withdraw()
                OMFITaux['pythonRunWindows'][0].resizable(tk.YES, tk.NO)
                OMFITaux['pythonRunWindows'][0].transient(OMFITaux['rootGUI'])
                OMFITaux['pythonRunWindows'][0].wm_title('Execution of OMFIT workflow...')
                OMFITaux['pythonRunWindows'][0].protocol("WM_DELETE_WINDOW", 'break')

        if OMFITaux['rootGUI'] is None or kw['noGUI'] or OMFITaux['pythonRunWindows'][-1] is None:
            OMFITaux['pythonRunWindows'].append(None)
        else:
            OMFITaux['pythonRunWindows'].append(ttk.Frame(OMFITaux['pythonRunWindows'][-1], borderwidth=2, relief=tk.GROOVE))

            text = treeLocation(self)[-1]
            if not text:
                text = os.path.split(str(self.filename))[1]
            frame = OMFITaux['pythonRunWindows'][-1]
            ttk.Label(frame, text=text).pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
            frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
            if IcreatedIt:
                OMFITaux['rootGUI'].update_idletasks()
                tk_center(OMFITaux['pythonRunWindows'][0], OMFITaux['rootGUI'])
                OMFITaux['pythonRunWindows'][0].deiconify()

            for item in _update_alarm:
                OMFITaux['rootGUI'].after_cancel(_update_alarm.pop())
            if IcreatedIt:
                OMFITaux['rootGUI'].update_idletasks()
            else:
                _update_alarm.append(OMFITaux['rootGUI'].after(100, OMFITaux['rootGUI'].update_idletasks))

        noGUI = OMFITaux['pythonRunWindows'][-1] is None
        return IcreatedIt, noGUI

    def _endGUI(self, IcreatedIt, success=True):
        if IcreatedIt and OMFITaux['haltWindow'] is not None:
            try:
                os.kill(OMFITaux['haltWindow'], 9)
            except Exception:
                pass
            OMFITaux['haltWindow'] = None

        if not len(OMFITaux['pythonRunWindows']):
            printd('Could not find pythonRunWindows in _endGUI.')
        elif OMFITaux['pythonRunWindows'][-1] is None:
            OMFITaux['pythonRunWindows'].pop()
            if IcreatedIt:
                OMFITaux['pythonRunWindows'].pop()
        else:
            frame = OMFITaux['pythonRunWindows'].pop()
            frame.destroy()
            if IcreatedIt:
                OMFITaux['pythonRunWindows'].pop().destroy()
                if success:
                    _streams['HIST'].write(
                        'Done @ '
                        + datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        + ' took {:.3f} s\n'.format(time.time() - IcreatedIt)
                    )
                # GUIs will be updated only when there are no more pythonRunWindows open
                if OMFITaux['rootGUI'] is not None:
                    OMFITaux['rootGUI'].event_generate("<<update_GUI>>")

            # make a tree update at the end of each execution
            if OMFITaux['rootGUI'] is not None:
                OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
                for item in _update_alarm:
                    OMFITaux['rootGUI'].after_cancel(_update_alarm.pop())
                if IcreatedIt:
                    OMFITaux['rootGUI'].update_idletasks()
                else:
                    _update_alarm.append(OMFITaux['rootGUI'].after(100, OMFITaux['rootGUI'].update_idletasks))

    def run(self, **kw):
        IcreatedIt = True
        success = False
        try:
            IcreatedIt, noGUI = self._startGUI(**kw)
            if IcreatedIt:
                start_mem = 0
                try:
                    import psutil
                except ImportError:
                    pass
                else:
                    start_mem = float(psutil.Process(os.getpid()).memory_info().rss)
                    printd('Starting memory=%d' % start_mem, topic='gc')

            # Multithreading disabled until further notice (see issue #4564)
            if False and not kw.get('defaultVarsGUI', False) and IcreatedIt and not noGUI:

                # Array used to keep a reference of OMFITpythonTask return
                result = []
                # Call method to execute __run__ on a new thread
                thread = threaded_logic(self.__run__, result, **kw)
                # Wait for the thread to finish
                while thread not in done_thread:
                    sleep(0.1)
                # Remove thread from done array and join
                done_thread.remove(thread)
                thread.join()
                # Assign result from thread
                if result[0] == 'OK':
                    result = result[1]
                else:
                    raise result[1]
            else:
                result = self.__run__(**kw)

            success = True
            return result

        finally:
            self._endGUI(IcreatedIt, success=success)
            if IcreatedIt:
                if start_mem > 0:
                    end_mem = float(psutil.Process(os.getpid()).memory_info().rss)
                    printd('Ending memory=%d' % end_mem, topic='gc')
                    if (end_mem - start_mem) / start_mem > 0.1:
                        printd('Running gc.collect', topic='gc')
                        import gc

                        gc.collect()

    def runNoGUI(self, **kw):
        """
        This method allows execution of the script without invoking TkInter commands
        Note that the TkInter commands will also be discarded for the OMFITpython scipts that this method calls
        """
        kw['noGUI'] = True
        return self.run(**kw)

    def prun(
        self,
        nsteps,
        nprocs,
        resultNames,
        noGUI=False,
        prerun='',
        postrun='',
        result_type=None,
        runIDs=None,
        runlabels=None,
        no_mpl_pledge=False,
        **kw,
    ):
        r"""
        Parallel execution of OMFITpythonTasks.

        >> a=OMFIT['test'].prun(10,5,'a',prerun="OMFIT['c']=a",a=np.arange(5)*2+0.5)

        :param nsteps: number of calls

        :param nprocs: number of simultaneous processes

        :param resultNames: name, or list of names with the variables that will be returned at the end of the execution of each script

        :param noGUI: Disable GUI with gray/blue/green boxes showing progress of parallel run

        :param prerun: string that is executed before each parallel execution (useful to set entries in the OMFIT tree)

        :param postrun: string that is executed after each parallel execution (useful to gather entries from the OMFIT tree)

        :param result_type: class of the object that will contain the `prun` results (e.g. `OMFITtree`, `OMFITcollection`, `OMFITmcTree`)

        :param runIDs: list of strings used to name and retrieve the runs (use numbers by default)

        :param runlabels: list of strings used to display the runs (same as runIDs by default)

        :param no_mpl_pledge: User pledges not to call any matplotlib plotting commands as part of their scripts.
                              The prun will thus not need to swithch the matplotlib backend, which would close any open figures.

        :param \**kw: additional keywords will appear as local variables in the user script
                      Local variables that are meant to change between different calls to the script should be passed as lists of length `nsteps`

        :return: Dictionary containing the results from each script execution
        """
        if result_type is None:
            result_type = OMFITtree
        if nsteps < 1:
            return result_type()

        if (
            OMFITaux['rootGUI'] is None
            or len(OMFITaux['prun_process'])
            or (len(OMFITaux['pythonRunWindows']) and OMFITaux['pythonRunWindows'][-1] is None)
        ):
            noGUI = True
        # backward compatibility
        runNoGUI = noGUI

        # human-readable run IDs and labels
        customids = True if runIDs is None else False
        if runIDs is None:
            step_name = list(range(nsteps))
        else:
            step_name = runIDs
        if runlabels is None:
            step_label = step_name
        else:
            step_label = runlabels

        # if there are nested parallel loops, make only the outermost parallel
        # if len(OMFITaux['prun_process']):
        #    nprocs=1
        myname = treeLocation(self)[-1]
        if not myname:
            myname = os.path.split(self.filename)[-1]
        printi('Starting parallel execution of ' + myname)

        try:
            if not noGUI:
                IcreatedIt, _ = self._startGUI()

                stopSpawning = tk.BooleanVar()

                def onAbort():
                    stopSpawning.set(True)
                    for k in range(nprocs):
                        printe(k, p[k])
                        if p[k] is not None and p[k].is_alive():
                            try:
                                os.kill(p[k].pid, signal.SIGTERM)
                            except OSError:
                                pass

                bt_abort = ttk.Button(OMFITaux['pythonRunWindows'][-1], text="Abort all", command=onAbort)
                bt_abort.pack()

                top0 = ttk.Frame(OMFITaux['pythonRunWindows'][-1])
                top0.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

                top = ttk.Frame(top0)
                top.place(in_=top0, anchor="s", relx=0.5, rely=1.0)

                progress = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='determinate')
                progress['value'] = 0
                progress['maximum'] = nsteps
                progress.grid(row=0, column=0, columnspan=100, padx=5, pady=5, sticky=tk.E + tk.W + tk.N + tk.S)
                maxr = 0
                maxc = 0
                n = int(np.ceil(np.sqrt(nsteps)))
                labels = [None] * nsteps
                for step in range(nsteps):
                    r = int(step // n)
                    c = step - r * n
                    labels[step] = ttk.Label(top, text=str(step_label[step])[:16], width=20 if customids else 8, state=tk.DISABLED)
                    labels[step].grid(row=r + 1, column=c, padx=1, pady=1)
                    maxr = max([r + 1, maxr])
                    maxc = max([c + 1, maxc])
                top0.update_idletasks()
                top0.configure(
                    width=maxc * (labels[step].winfo_width() + 2),
                    height=maxr * (labels[step].winfo_height() + 2) + progress.winfo_height() + 10,
                )

            steps = list(range(nsteps))
            results = result_type()
            step = [None] * nprocs
            p = [None] * nprocs
            p_alive = [0] * nprocs
            allDone = [0]

            def runProcess(nprocs, process_id, nsteps, step_id, kw):
                whatHappened = ''
                OMFITaux['pythonRunWindows'] = [None]
                OMFITaux['prun_process'].append(process_id)
                OMFITaux['prun_nprocs'].append(nprocs)

                try:
                    # force different seed initialization for random processes
                    # here we purposly use Python's native __hash__ function
                    # which returns an integer
                    pylab.seed(omfit_numeric_hash(str(time.time()), 10) * (step_id + 1) % 4294967295)
                    kw.update(
                        {
                            'nprocs': nprocs,
                            'process_id': process_id,
                            'nsteps': nsteps,
                            'step_id': step_id,
                            'step_name': str(step_name[step_id]),
                        }
                    )
                    if len(prerun):
                        kw['strict_defaultVars'] = False
                    tmp = self.__run__(prerun=prerun, postrun=postrun, **kw)

                    process_results = OMFITtree()
                    if resultNames:
                        if isinstance(resultNames, str):
                            process_results = tmp[resultNames]
                        else:
                            for resultName in resultNames:
                                process_results[resultName] = tmp[resultName]
                    retcode = 0

                except Exception as _excp:
                    process_results = _excp
                    etype, value, tb = sys.exc_info()
                    excpStack = traceback.format_exception(etype, value, tb)
                    whatHappened = '\n' + '\n'.join(excpStack) + '\n'
                    retcode = -1

                # pickle process results
                filename = OMFITcwd + os.sep + 'pickle_' + '_'.join(map(str, OMFITaux['prun_process']))
                try:
                    with open(filename, 'wb') as f:
                        pickle.dump(
                            [retcode, process_results, sys.stdout.getvalue(), sys.stderr.getvalue() + whatHappened],  # actual results
                            f,
                            pickle.HIGHEST_PROTOCOL,
                        )
                except Exception as exc:
                    printe('Failed to pickle results:', repr(exc))
                    with open(filename, 'wb') as f:
                        pickle.dump(
                            [retcode, exc, sys.stdout.getvalue(), sys.stderr.getvalue() + whatHappened],  # resulting exception
                            f,
                            pickle.HIGHEST_PROTOCOL,
                        )

            def pManager(progressBarToggle):
                for k in range(nprocs):
                    if p[k] is not None:
                        p_alive[k] = int(p[k].is_alive())
                    else:
                        p_alive[k] = 0

                # retrieval
                while np.any([(p_alive[kk] == 0 and step[kk] is not None) for kk in range(len(p_alive))]):
                    k = [(p_alive[kk] == 0 and step[kk] is not None) for kk in range(len(p_alive))].index(True)

                    # unpickle process results
                    excp = ''
                    try:
                        filename = OMFITcwd + os.sep + 'pickle_' + '_'.join(map(str, OMFITaux['prun_process'] + [k]))
                        with open(filename, 'rb') as f:
                            retcode, results[step_name[step[k]]], stdout, stderr = pickle.load(f)
                        os.remove(filename)
                    except Exception as _excp:
                        results[step_name[step[k]]] = _excp
                        retcode = -1
                        stdout = []
                        stderr = []
                        excp = repr(_excp)

                    if not noGUI:
                        if retcode:
                            labels[step[k]].config(background='indianRed1')
                        else:
                            labels[step[k]].config(background='chartreuse3')
                    _streams['INFO'].write('===============================\n')
                    _streams['INFO'].write('-->   STEP {s} OF {n}\n'.format(s=step[k] + 1, n=nsteps))
                    _streams['INFO'].write('===============================\n')
                    if stdout:
                        _streams['PROGRAM_OUT'].write(''.join(stdout) + '\n')
                    if stderr:
                        _streams['PROGRAM_ERR'].write(''.join(stderr) + '\n')
                    if excp:
                        _streams['STDERR'].write(excp + '\n')

                    step[k] = None
                    p[k] = None

                # start new
                while len(steps) and not np.all(p_alive):
                    k = p_alive.index(0)
                    if nsteps <= nprocs:
                        step[k] = steps.pop(0)
                    else:
                        # shuffle run step for load balancing purposes
                        step[k] = steps.pop(pylab.randint(len(steps)))

                    # generate input dictionary
                    kw0 = {}
                    for kk in list(kw.keys()):
                        try:
                            if isinstance(kw[kk], str):
                                raise TypeError()
                            kw0[kk] = kw[kk][step[k]]
                        except Exception:
                            kw0[kk] = kw[kk]

                    with parallel_environment(mpl_backend=not no_mpl_pledge):
                        p[k] = multiprocessing.Process(target=runProcess, args=(nprocs, k, nsteps, step[k], kw0))
                        p[k].start()
                        p_alive[k] = int(p[k].is_alive())

                    if not noGUI:
                        text = str(step_label[step[k]])[:16]
                        if nprocs < nsteps or customids:
                            text += ' (%d)' % k
                        labels[step[k]].config(background='dodger blue', text=text, state=tk.NORMAL)

                # check if everything was all done
                if allDone[0] == 0 and not len(steps) and not np.any([step[kk] is not None for kk in range(len(p_alive))]):
                    allDone[0] = 1

                # stop spawning if Abort all
                if not noGUI and stopSpawning.get():
                    allDone[0] = -1
                    while len(steps):
                        steps.pop()
                    return

                if not noGUI:
                    progress['value'] = nsteps - len(steps) - np.sum(p_alive) * progressBarToggle

            # toggle between completed and active processes in progressBar
            progressBarToggle = False

            # while there are still some steps to be run or there are processes running
            T = time.time()
            while allDone[0] == 0:
                sleep(0.01)
                pManager(progressBarToggle)
                if time.time() - T > 0.5:
                    progressBarToggle = not progressBarToggle
                    T = time.time()
        finally:
            if not noGUI:
                top.destroy()
                self._endGUI(IcreatedIt)

        if allDone[0] > 0:
            myname = treeLocation(self)[-1]
            if not myname:
                myname = os.path.split(self.filename)[-1]
            printi('Ended parallel execution of ' + myname)
            sorted_results = result_type()
            for item in step_name:
                sorted_results[item] = results[item]
            return sorted_results
        else:
            raise EndAllOMFITpython('\n\n---> Aborted by user <---\n\n')

    def opt(
        self,
        actuators,
        targets,
        reset=None,
        prerun='',
        postrun='',
        method='hybr',
        tol=None,
        options={'xtol': 1e-2, 'eps': 1e-2},
        postfail='',
        reset_on_fail=True,
        **kw,
    ):
        r"""
        Execute OMFITpythonTask using inside scipy.optimize.root
            Optimizes actuators to achieve targets
            Any tree location in the reset list is reset on each call to self
            Tree will be in the state after the final run of self, whether the
            optimizer converges or not.  If there is an exception, tree is reset
            using the reset list.
            *See regression/test_optrun.py for example usage

        :arg actuators: dictionary of actuator dictionaries with the following keys
                        'set': function or string tree location to set as actuator
                        'init': initial value for actuator

        :arg targets: dictionary of target dictionaries with the following keys
                      'get': function or string tree location to get current value
                      'target': value to target
                      'tol': (optional) absolute tolerance of target value

        :param reset: list of tree locations to be reset on each iteration of optimization

        :param prerun: string that is executed before each execution of self
                       *useful for setting entries in the OMFIT tree

        :param postrun: string that is executed after each execution of self
                        *useful for gathering entries from the OMFIT tree

        :param method: keyword passed to scipy.optimize.root

        :param tol: keyword passed to scipy.optimize.root

        :param options: keyword passed to scipy.optimize.root

        :param postfail: string that is executed if execution of self throws an error
                         *useful for gathering entries from the OMFIT tree

        :param reset_on_fail:  reset the tree if an exception or keyboard interrupt occurs

        :param \**kw: additional keywords passed to self.run()

        :return: OptimizeResult output of scipy.optimize.root,
                 Convergence history of actuators, targets, and errors
        """

        # setup and store local namespace to pass into vector_opt
        _relLoc = relativeLocations(self)

        cache = {'x': None, 'errors': None}
        resets = {}
        convergence = {'actuators': {}, 'targets': {}, 'error': []}
        for actuator in list(actuators.keys()):
            convergence['actuators'][actuator] = []
        for target in list(targets.keys()):
            convergence['targets'][target] = []

        def vector_opt(x, resets, cache, convergence):

            locals().update(_relLoc)

            # return cached values if same as last iteration
            try:
                cached = (x == cache['x']).all()
            except AttributeError:
                cached = x == cache['x']
            if cached:
                printi("Using cached values")
                return copy.deepcopy(cache['errors'])

            # reset tree as necessary
            def reset_tree(resets):
                locals().update(_relLoc)
                for loc in list(resets.keys()):
                    if loc == 'root':
                        # can't reset root itself, so traverse and deepcopy
                        for key in _relLoc['root']:
                            if key not in resets[loc]:
                                del _relLoc['root'][key]
                            else:
                                _relLoc['root'][key] = copy.deepcopy(resets[loc][key])
                    else:
                        exec(loc + "=copy.deepcopy(resets[loc])", globals(), locals())
                return

            reset_tree(resets)

            try:
                # set actuator values
                for i, actuator in enumerate(actuators.keys()):
                    convergence['actuators'][actuator].append(x[i])
                    set_act = actuators[actuator]['set']
                    if callable(set_act):
                        # set as function
                        set_act(x[i])
                    else:
                        # set as tree location
                        exec(set_act + " = x[i]", globals(), locals())

                # run self with current values x of actuators
                exec(prerun, globals(), locals())
                self.run(_relLoc=_relLoc, **kw)
                exec(postrun, globals(), locals())

                # calculate error from targets
                errors = []
                for target in list(targets.keys()):
                    current = targets[target]['get']
                    if callable(current):
                        current = current()
                    else:
                        current = eval(current)
                    convergence['targets'][target].append(current)
                    errors.append(targets[target]['target'] - current)
                errors = np.array(errors)
                convergence['error'].append(errors)
                cache['x'] = copy.deepcopy(x)
                cache['errors'] = copy.deepcopy(errors)

                for i, target in enumerate(list(targets.keys())):
                    if 'tol' not in targets[target]:
                        continue
                    if abs(errors[i]) <= targets[target]['tol']:
                        # We've found a root within tol, so set to zero
                        errors[i] = 0.0

                return errors

            except (Exception, KeyboardInterrupt):
                exec(postfail, globals(), locals())
                if reset_on_fail:
                    # ensure tree returns to workable state if there's an exception
                    reset_tree(resets)
                raise

        # get initial guesses
        x0 = []
        for actuator in list(actuators.keys()):
            x0.append(actuators[actuator]['init'])

        # setup reset
        if reset is not None:
            root = _relLoc['root']
            for loc in reset:
                resets[loc] = copy.deepcopy(eval(loc))

        # optimize
        from scipy import optimize

        sol = optimize.root(vector_opt, x0, (resets, cache, convergence), method=method, tol=tol, options=options)

        # convert convergence values to np.ndarray
        convergence['error'] = np.array(convergence['error'])
        for actuator in list(convergence['actuators'].keys()):
            convergence['actuators'][actuator] = np.array(convergence['actuators'][actuator])
        for i, target in enumerate(list(convergence['targets'].keys())):
            convergence['targets'][target] = np.array(convergence['targets'][target])
            if 'tol' in targets[target]:
                # restore to actual error values
                err = targets[target]['target'] - convergence['targets'][target]
                convergence['error'][:, i] = err
                sol['fun'][i] = err[-1]

        opt_sol = OMFITjson('opt_sol.json')
        opt_sol.update(sol)

        opt_conv = OMFITjson('opt_conv.json')
        opt_conv.update(convergence)

        return opt_sol, opt_conv

    def importCode(self, **kw):
        """
        Executes the code and returns it as newly generated module

        >> myLib=OMFIT['test'].importCode()
        >> print myLib.a
        """
        import types

        module = types.ModuleType('OMFITpythonTask_' + str(id(self)))
        module.__dict__.update(self.__run__(**kw))
        return module


class OMFITpythonGUI(_OMFITpython):
    """Python script for OMFIT gui"""

    def __init__(self, filename, **kw):
        _OMFITpython.__init__(self, filename, **kw)

    def run(self, _relLoc=None, **kw):
        # allow only one GUI instance from this OMFITpythonGUI object
        if kw.pop('singleGUIinstance', True):
            for item in list(OMFITx._GUIs.keys()):
                if id(self) == id(OMFITx._GUIs[item].pythonFile):
                    OMFITx._clearClosedGUI(OMFITx._GUIs[item].top)

        if _relLoc is None:
            _relLoc = relativeLocations(self)

        oldDir = os.getcwd()
        try:
            OMFITx.GUI(self, _relLoc, **kw)
        finally:
            os.chdir(oldDir)
            # make a tree update at the end of each execution
            if OMFITaux['rootGUI'] is not None:
                OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
                OMFITaux['rootGUI'].update_idletasks()

    def __call__(self, **kw):
        self.run(**kw)


class OMFITpythonPlot(_OMFITpython):
    """
    Python script for OMFIT plots.
    Differently from the OMFITpythonTask class, the OMFITpythonPlot will not refresh the OMFIT GUIs
    though the OMFIT tree GUI itself will still be updated.

    Use .plot() method for overplotting (called by pressing <Shift-Return> in the OMFIT GUI)

    Use .plotFigure() method for plotting in new figure (called by pressing <Return> in the OMFIT GUI)

    When a single script should open more than one figure, it's probably best to use objects
    of the class :class:`OMFITpythonTask` and manually handling oveplotting and opening of new figures.
    To use a OMFITpythonTask object for plotting, it's useful to call the .runNoGUI method
    which prevents update of the GUIs that are open.
    """

    _header = '''"""
This script <fill in purpose>

defaultVars parameters
----------------------
param fig: None or matplotlib Figure instance. If None, a new figure will be created and assigned to 'fig' in this scripts namespace.
"""

defaultVars(fig=None)

'''

    def __init__(self, filename, **kw):
        _OMFITpython.__init__(self, filename, **kw)

    def __call__(self, **kw):
        return self.plot(**kw)

    def run(self, **kw):
        printw(
            os.path.split(self.filename)[1]
            + ': .run() method will be discontinued for OMFITpythonPlot objects.\nPlease use .plot() or .plotFigure() instead.'
        )
        return self.plot(**kw)

    def runNoGUI(self, **kw):
        printw(
            os.path.split(self.filename)[1]
            + ': .runNoGUI() method will be discontinued for OMFITpythonPlot objects. \nPlease use .plot() or .plotFigure() instead.'
        )
        return self.plot(**kw)

    def plot(self, **kw):
        r"""
        Execute the script and open a new figure only if no figure was already open.
        Effectively, this will result in an overplot.
        This method is called by pressing <Shift-Return> in the OMFIT GUI.

        :param \**kw: keywords passed to the script
        """
        oldDir = os.getcwd()
        try:
            kw['noGUI'] = True
            return self.__run__(**kw)
        finally:
            if hasattr(OMFITaux['rootGUI'], 'event_generate'):
                OMFITaux['rootGUI'].event_generate("<<update_treeGUI>>")
                OMFITaux['rootGUI'].update_idletasks()
            os.chdir(oldDir)

    def plotFigure(self, *args, **kw):
        r"""
        Execute the script and open a new figure.
        Effectively, this will result in a new figure.
        This method is called by pressing <Return> in the OMFIT GUI.

        :param \*args: arguments passed to the figure() command

        :param \**kw: keywords passed to the script
        """
        if 'fig' in kw:
            fig = kw.pop('fig')
        else:
            fig = pyplot.figure(*args)
        return self.plot(fig=fig, **kw)


class OMFITpythonTest(OMFITpythonTask):
    """
    Python script for OMFIT regression tests
    """

    def __init__(self, filename, **kw):
        if not os.path.exists(filename):
            if os.path.dirname(filename) == '':
                src_dir = f'{os.path.abspath(os.path.dirname(__file__))}/../..'
                reg_dir = f'{src_dir}/regression/'
                if os.access(reg_dir, os.W_OK) and not os.path.exists(f'{src_dir}/public'):
                    filename = reg_dir + filename
                    kw['modifyOriginal'] = True
                    if not os.path.exists(filename):
                        name = 'test_'.join(os.path.basename(filename[:-3]).split('test_')[1:])
                        with open(filename, 'w') as f:
                            f.write(self._header.format(name=name))
        OMFITascii.__init__(self, filename, **kw)
        if not os.path.basename(filename).startswith('test_') or not os.path.basename(filename).endswith('.py'):
            raise OMFITexception(
                f'Invalid filename: `{filename}` OMFITpythonTest objects filename must start with `test_` and have .py extension'
            )
        if not os.stat(self.filename).st_size:
            with open(self.filename, 'w') as f:
                name = 'test_'.join(os.path.basename(filename[:-3]).split('test_')[1:])
                f.write(self._header.format(name=name))

        self._done_tidy = False

    _header = '''"""
labels: ['framework', 'classes', 'modules', 'gui', 'short', 'medium', 'long', ...]
modules: ['EFIT', '...']

options: # How different options in labels affect running parameters
  - labels: ['-gui']
    params: {{allow_gui: False}}

**************************************

Do not delete separator above.
Docstring about what this regression test goes here.

:param someVariable: explain variables passed to defaultVars here

"""

from omfit_classes.omfit_testing import OMFITtest, manage_tests, standard_test_keywords

standard_test_keywords['run_tests'] = __name__ in ['__main__', 'omfit_classes.omfit_python']
dfv = defaultVars(**standard_test_keywords)


class Test_{name}(OMFITtest):

    def test_case1(self):
        """first test goes here"""
        pass

    def test_case2(self):
        """second test goes here"""
        pass


if dfv.pop('run_tests'):
    manage_tests(Test_{name:}, **dfv)

'''

    def tests_list(self):
        """
        :return: list of available tests
        """
        these = []
        with open(self.filename, 'r') as f:
            lines = f.read()
        for line in lines.split('\n'):
            if line.startswith('    def test_'):
                these.append(line.split('(')[0].split('def ')[1])
        return these


class parallel_environment(object):
    """
    This environment is used as part of OMFITpythonTask.prun to make it safe for multiprocessing
    """

    def __init__(self, mpl_backend=None):
        if mpl_backend and not isinstance(mpl_backend, str):
            mpl_backend = 'agg'
        self.mpl_backend = mpl_backend

    def __enter__(self):
        if self.mpl_backend:
            self.old_mpl_backend = matplotlib.get_backend()
            pyplot.switch_backend(self.mpl_backend)
        self.streams_bkp = {}
        self.streams_bkp.update(_streams)
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        for k in _streams:
            if 'ERR' in k:
                _streams[k] = sys.stderr
            else:
                _streams[k] = sys.stdout
        return self.streams_bkp

    def __exit__(self, type, value, traceback):
        _streams.update(self.streams_bkp)
        _streams['STDOUT'].write(sys.stdout.getvalue())
        _streams['STDERR'].write(sys.stderr.getvalue())
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = _streams['STDOUT']
        sys.stderr = _streams['STDERR']
        if self.mpl_backend:
            pyplot.switch_backend(self.old_mpl_backend)


# ---------------------
# threading
# ---------------------
# Arrays to keep track of active and dead threads
logic_thread = []
done_thread = []

# Create new thread and run command in it
def threaded_logic(function, result, *args, **kw):
    def threaded_function():
        if not isinstance(result, list) or len(result):
            raise Exception('threaded_logic result must be an empty list')
        try:
            result[:] = ['OK', function(*args, **kw)]
        except (Exception, EndOMFITpython, EndAllOMFITpython) as _excp:
            result[:] = ['ERROR', _excp]
        finally:
            logic_thread.remove(threading.current_thread())
            done_thread.append(threading.current_thread())

    if len(logic_thread) > 2:  # Limit number of threads
        print('Wait for previous OMFIT task to complete')
        return
    else:
        # Create new Thread and run selected method in it
        thread = threading.Thread(target=threaded_function)
        # Add new thread to active array
        logic_thread.append(thread)
        logic_thread[-1].start()
        # Return Thread so active tasks can be displayed on the GUI
        return thread


# ---------------------
# Documentation
# ---------------------
class omfit_pydocs(SortedDict):
    def __init__(self):
        SortedDict.__init__(self)

    def _buildGUI(self, parent, topLevel=True):
        self._buildDocs()
        self.parent = parent

        if topLevel:
            self.top = top = tk.Toplevel(parent)
            top.withdraw()
            top.transient(parent)
            top.wm_title("OMFIT HELP window")
            top.protocol("WM_DELETE_WINDOW", self.destroy)
            top.bind(f'<{ctrlCmd()}-h>', lambda event=None: self.destroy())
        else:
            self.top = top = parent

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        ttk.Label(frm, text='Look for :').pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=5, pady=5)
        self.e = ttk.Entry(frm)
        self.e.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=5, pady=5)
        self.b = ttk.Button(frm, text="Online API documentation", command=lambda event=None: openInBrowser('https://omfit.io/code.html'))
        self.b.pack(side=tk.LEFT, expand=tk.NO, fill=tk.NONE, padx=5, pady=5)

        def doSomething(event=None):
            tab_selected = self.notebook.tab(self.notebook.tabs().index(self.notebook.select()))['text']
            for k in self.t:
                self.t[k].pack_forget()
            if tab_selected == 'Documentation':
                self.t['Documentation'].pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
            elif tab_selected == 'Attributes':
                self.t['Attributes'].pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
            elif tab_selected == 'Source code':
                self.t['Source'].pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
            elif tab_selected == 'Related':
                self.t['Related'].pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        self.notebook = ttk.Notebook(top)
        self.notebook.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.notebook.add(ttk.Frame(top), text='Documentation')
        self.notebook.add(ttk.Frame(top), text='Attributes')
        self.notebook.add(ttk.Frame(top), text='Source code')
        self.notebook.add(ttk.Frame(top), text='Related')
        self.notebook.bind("<<NotebookTabChanged>>", doSomething)

        self.t = {}
        self.t['Documentation'] = tk.ScrolledText(
            top, wrap=tk.NONE, undo=tk.TRUE, maxundo=-1, relief=tk.GROOVE, border=1, height=24, font=OMFITfont(family='courier')
        )
        self.t['Attributes'] = tk.ScrolledText(
            top,
            wrap=tk.NONE,
            undo=tk.TRUE,
            maxundo=-1,
            relief=tk.GROOVE,
            border=1,
            height=24,
            percolator=False,
            font=OMFITfont(family='courier'),
        )
        self.t['Source'] = tk.ScrolledText(
            top,
            wrap=tk.NONE,
            undo=tk.TRUE,
            maxundo=-1,
            relief=tk.GROOVE,
            border=1,
            height=24,
            percolator=True,
            font=OMFITfont(family='courier'),
        )
        self.t['Related'] = tk.ScrolledText(
            top, wrap=tk.NONE, undo=tk.TRUE, maxundo=-1, relief=tk.GROOVE, border=1, height=24, font=OMFITfont(family='courier')
        )

        if topLevel:
            for item in self.t:
                self.t[item].set(f'\n\n\t\tUse <{ctrlCmd()}-h> to show/hide this help window')

        if topLevel:
            menubar = tk.Menu(top)
            for item in list(self.keys()):
                submenu = tk.Menu(menubar, tearoff=False)
                if isinstance(self[item], list):
                    for subitem in self[item]:
                        submenu.add_command(label=subitem, command=lambda subitem=subitem: self(subitem))
                elif isinstance(self[item], dict):
                    for subitem in self[item]:
                        if self[item][subitem] is None:
                            submenu.add_command(label=subitem, command=lambda subitem=subitem: self(subitem))
                        else:
                            sub_menu = tk.Menu(submenu, tearoff=False)
                            for sub_item in self[item][subitem]:
                                sub_menu.add_command(label=sub_item, command=lambda sub_item=sub_item: self(sub_item))
                            submenu.add_cascade(label=subitem, menu=sub_menu)
                menubar.add_cascade(label=re.sub('Documentation: ', '', item), menu=submenu, underline=0)

            top.config(menu=menubar)

        self.e.bind('<Return>', lambda event=None: self(self.e.get()))
        self.e.bind('<KP_Enter>', lambda event=None: self(self.e.get()))

        if topLevel:
            self.e.bind(f'<{ctrlCmd()}-h>', lambda event=None: self.destroy())
            for k in self.t:
                self.t[k].bind(f'<{ctrlCmd()}-h>', lambda event=None: self.destroy())

    def _buildDocs(self):
        tmp = list(
            [inspect.getmodule(x).__name__ + '.' + x.__name__ for x in tuple(OMFITtypes + OMFITdictypes + [OMFITmdsValue, OMFITexpression])]
        )
        tmp.sort(key=lambda x: str(x).lower())
        tmpd = OrderedDict()
        if True:
            # sort my file where it is contained
            for item in tmp:
                items = item.split('.')
                if items[0] == 'omfit_classes':
                    tmpd.setdefault(items[1], [])
                    tmpd[items[1]].append(items[-1])
                else:
                    tmpd[items[-1]] = None
        else:
            # sort by base class
            for item in tmp:
                items = item.split('.')
                assigned = False
                for test in ['OMFITascii', 'OMFITobject', 'SortedDict']:
                    if issubclass(eval(items[-1]), eval(test)):
                        assigned = True
                        tmpd.setdefault(test, [])
                        tmpd[test].append(items[-1])
                        break
                if not assigned:
                    tmpd[items[-1]] = None

        self['Documentation: Classes'] = tmpd
        self['Documentation: Tasks'] = ['OMFITx.' + k.__name__ for k in OMFITaux['OMFITxTASK_functions']]
        self['Documentation: Tasks'].extend(['defaultVars', 'OMFITworkDir'])
        self['Documentation: GUIs'] = ['OMFITx.' + k.__name__ for k in OMFITaux['OMFITxGUI_functions']]
        self['Documentation: Plots'] = list(set([k.__name__ for k in OMFITaux['OMFITplot_functions']]))
        self['Documentation: Utils'] = list(set([k.__name__ for k in OMFITaux['OMFITutil_functions']]))
        self['Documentation: Math'] = list(set([k.__name__ for k in OMFITaux['OMFITmath_functions']]))
        self['Documentation: Fusion'] = ['utils_fusion.' + k.__name__ for k in OMFITaux['OMFITfusion_functions']]
        for item in self:
            if isinstance(self[item], list):
                self[item].sort(key=lambda x: str(x).lower())

    def destroy(self):
        self.top.withdraw()
        return 'break'

    def __call__(self, item=special1):
        helpstring, item, item_str, related, source, attributes = self._helpstring(item)

        if not hasattr(self, 'parent') and item is not special1:
            tag_print(helpstring, tag='HELP')
        else:
            if item is not special1:
                self.e.delete(0, tk.END)
                self.e.insert(0, item_str)
                self.t['Documentation'].set(helpstring)
                self.t['Attributes'].set(attributes)
                self.t['Source'].set(source)
                self.t['Related'].set(related)
            self.e.focus_set()
            if isinstance(self.top, tk.Toplevel):
                self.top.deiconify()

    def _helpstring(self, item=special1):
        helpstring = ''
        item_str = ''
        related = ''

        if item is not special1:
            if isinstance(item, str):
                item_str = item
                try:
                    if item_str in ['.'.join(x) for x in list(omfit_classes.omfit_dmp.originals.keys())]:
                        item = omfit_classes.omfit_dmp.originals[tuple(item_str.split('.'))]
                    else:
                        item = eval(item_str)
                except Exception:
                    item = special1
            elif hasattr(item, '__name__'):
                item_str = item.__name__

            if item is not special1:
                helpstring = ''
                if not (inspect.ismodule(item) or inspect.isclass(item) or inspect.isfunction(item) or inspect.ismethod(item)):
                    helpstring = "\n\n%s is an object of type %s\n\n\n" % (repr(item_str), type(item))
                    item = type(item)
                helpstring += '\n'.join(re.sub('\b.', '', pydoc.render_doc(item)).split('\n')[1:]).strip()
            else:
                item = None
                helpstring = "\n\n%s is not defined within the OMFIT realm" % repr(item_str)

        # reverse documentation lookup
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            docs = {}
            for k in list(globals().keys()):
                if hasattr(globals()[k], '__doc__'):
                    try:
                        docs[str(globals()[k].__doc__)] = str(k)
                    except Exception:
                        pass
                for kk in dir(globals()[k]):
                    try:
                        docs[str(getattr(globals()[k], kk).__doc__)] = str(k) + '.' + str(kk)
                    except Exception:
                        pass

        direct = set([d for d in list(globals().keys()) if item_str.lower() in d.lower()])
        inverse = set([docs[d] for d in list(docs.keys()) if item_str.lower() in d.lower()])
        inverse = inverse.difference(direct)
        direct = direct.difference(set([item_str]))
        inverse = inverse.difference(set([item_str]))

        n = 30
        if len(direct):
            related += '=' * n + "\nPerhaps you were looking for:\n" + '=' * n + '\n '
            related += '\n '.join([('*' * (x.count('.') + 1)).rjust(2) + ' ' + x for x in sorted(direct)]) + '\n\n'
        if len(inverse):
            related += '=' * n + "\nRelated topics:\n" + '=' * n + '\n '
            tmp = [k for k in sorted(inverse) if '.' not in k]
            if len(tmp):
                related += '\n '.join([('*' * (x.count('.') + 1)).rjust(2) + ' ' + x for x in tmp]) + '\n '
            tmp = [k for k in sorted(inverse) if '.' in k]
            if len(tmp):
                related += '\n '.join([('*' * (x.count('.') + 1)).rjust(2) + ' ' + x for x in tmp]) + '\n '
        if not len(related):
            related = '\n\n\tWe could not find any topic related to %s' % repr(item_str)

        try:
            source = '# excerpt from: ' + inspect.getsourcefile(item)
            source = '#' * len(source) + '\n' + source + '\n' + '#' * len(source) + '\n\n'
        except Exception:
            source = ''
        try:
            source += inspect.getsource(item)
        except Exception:
            source = "\n\n\tWe couldn`t find the source code of %s" % repr(item_str)

        def attr_line(attr):
            line = '.' + attr
            if callable(getattr(item, attr)):
                line += '(...)'
            line = line.ljust(n + 5) + ' '.join(str(type(getattr(item, attr))).split(' ')[1:]).strip('\'"><')
            return line

        try:
            n = max([len(attr) for attr in list(item.__dict__.keys())])
            attributes = [
                attr_line(attr)
                for attr in sorted(item.__dict__.keys())
                if not re.match(hide_ptrn, attr) and not re.match(private_ptrn, attr)
            ]
            attributes += [attr_line(attr) for attr in sorted(item.__dict__.keys()) if re.match(hide_ptrn, attr)]
            attributes += [attr_line(attr) for attr in sorted(item.__dict__.keys()) if re.match(private_ptrn, attr)]
            attributes = '\n'.join(attributes)
        except Exception:
            attributes = "\n\n\tWe couldn`t find the attributes for %s" % repr(item_str)

        return helpstring, item, item_str, related, source, attributes


# replace help method
help = omfit_pydocs()

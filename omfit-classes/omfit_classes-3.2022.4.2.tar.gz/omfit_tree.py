import warnings

import time

_t0 = time.time()

import sys
import os as _os

# ensure that any `import omfit.xxx` refers to this installation of OMFIT
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from omfit_classes.startup_framework import *

# import utilities
from utils import _available_to_user_math, _available_to_user_util, _available_to_user_plot, _available_to_user_fusion

# ---------------------
# classes under the `class` folder and starting with OMFIT
# ---------------------
_loaded_omfit_class_files = []

import omfit_classes.omfit_base
from omfit_classes.omfit_base import *
from omfit_classes.omfit_base import _moduleAttrs, itemTagsValues
from omfit_classes import unix_os as os

# override sys.exit to prevent external packages from quitting the session
_exit = sys.exit
sys.exit = lambda *args, **kw: None

import omfit_classes.omfit_python
from omfit_classes.omfit_python import *


_k = 0
for _file in sorted(glob.glob(OMFITsrc + '/omfit_classes/omfit_*.py')):
    _python_module = os.path.splitext(os.path.split(_file)[1])[0]
    try:
        exec("import omfit_classes." + _python_module, globals(), locals())
        try:
            getattr(omfit_classes, _python_module).__all__
        except AttributeError:
            raise OMFITexception(
                'Exception in omfit/%s: OMFIT does not allow modules under omfit/classes'
                'not to have an __all__ attribute which explicitly specifies what symbols '
                'will be exported when from <module> import * is used on the module' % _python_module
            )

        # all classes must be available in omfit_base and omfit_python since that's where the OMFITtree is defined
        if _python_module != 'omfit_base':
            for item in getattr(omfit_classes, _python_module).__all__:
                setattr(omfit_classes.omfit_base, item, getattr(getattr(omfit_classes, _python_module), item))

        if _python_module != 'omfit_python':
            for item in getattr(omfit_classes, _python_module).__all__:
                setattr(omfit_classes.omfit_python, item, getattr(getattr(omfit_classes, _python_module), item))

        exec("from omfit_classes import " + _python_module, globals(), locals())
        exec("from omfit_classes." + _python_module + ' import *', globals(), locals())
        _k += 1
        _loaded_omfit_class_files.append(('%2d)%s' % (_k, _python_module.replace('omfit_', ''))).ljust(20))
    except Exception:
        printe('Offending module: ' + _python_module)
        raise
sys.exit = _exit

for item in omfit_classes.omfit_python.__all__:
    setattr(omfit_classes.omfit_base, item, getattr(omfit_python, item))

# backward compatibility with old classes location in `classes` folder instead of `omfit_classes`
for item in list(sys.modules.keys()):
    if item.startswith('omfit_classes.'):
        # allow `import classes.omfit_classname` # how Python environment with local OMFIT installation can use OMFIT classes
        sys.modules[re.sub('^omfit_classes\.', 'classes.', item)] = sys.modules[item]

print('Loaded OMFIT classes:')
while len(_loaded_omfit_class_files):
    print(''.join(_loaded_omfit_class_files[:4]))
    _loaded_omfit_class_files = _loaded_omfit_class_files[4:]


def reload_python(moduleName, quiet=False):
    """
    This function extends the Python builtin `reload` function to easily reload OMFIT classes

    >>> reload_python(omfit_classes.omfit_onetwo)

    :param moduleName: module or module name

    :param quiet: bool
        Suppress print statements listing reloaded objects
    """
    from matplotlib.cbook.deprecation import MatplotlibDeprecationWarning

    warnings.filterwarnings('ignore', category=MatplotlibDeprecationWarning)
    if not isinstance(moduleName, str):
        moduleName = moduleName.__name__
    if not (moduleName.startswith('omfit_') or moduleName.startswith('omfit_classes.omfit_')):
        printe('reload_python is meant for class containing modules (in omfit_classes) that start with `omfit_`')
        printe('Try instead:\n\nreload({0})\nfrom {0} import *'.format(moduleName))
        return
    if moduleName in ['omfit_tree', 'omfit_gui']:
        printe('Can not reload omfit_tree or omfit_gui')
        return

    tmp = {}
    exec("import %s" % moduleName, tmp)
    from importlib import reload

    reload(eval(moduleName))
    exec("from " + moduleName + " import *", tmp)

    # Keep track of reloaded objects to avoid storing them in the persistent OMFITconsoleDict namespace
    OMFITreloadedDict.update(tmp)

    # Find objects in the OMFIT tree that should be reloaded
    OMtr = traverse(OMFIT, string='OMFIT', onlyDict=True, skipDynaLoad=True)
    OMtr_cls = {}
    for loc in OMtr:
        if hasattr(eval(loc), '__class__') and eval(loc).__class__.__name__ in list(tmp.keys()):
            OMtr_cls.setdefault(eval(loc).__class__.__name__, []).append(loc)

    # Select only the items that should be reloaded
    items = list(tmp.keys())
    if hasattr(eval(moduleName), '__all__'):
        items = eval(moduleName).__all__
    if '__builtins__' in items:
        items.remove('__builtins__')

    # Loop through items to reload
    updated = {}
    for item in items:
        # Loop through python modules
        for mod in list(sys.modules.keys()):
            if hasattr(sys.modules[mod], '__dict__') and item in sys.modules[mod].__dict__:
                sys.modules[mod].__dict__[item] = tmp[item]
                updated.setdefault(mod, []).append(item)
        # Loop through OMFIT objects
        if item in OMtr_cls:
            for loc in OMtr_cls[item]:
                if not quiet:
                    print(loc)
                eval(loc).__class__ = tmp[item]

    # Update OMFIT data types
    omfit_classes.omfit_base._updateTypes()

    if not quiet:
        printi('*' * 20)
        printi('Updated python modules')
        printi('*' * 20)
        pprinti(updated)
        printi('')
        printi('*' * 20)
        printi('Updated OMFIT tree entries')
        printi('*' * 20)
        pprinti(OMtr_cls)
    return


omfit_classes.omfit_python.reload_python = reload_python

# ---------------------
# OMFIT main tree
# ---------------------
_availableModulesCache = {}


class OMFITmaintree(OMFITproject):

    _save_method = '_save_with_info'

    def __init__(self, filename=''):
        OMFITproject.__init__(self, filename)
        self._OMFITparent = None
        self._OMFITkeyName = ''
        self.prj_options = {}

    def start(self, filename=''):
        self.clear()
        self.filename = filename
        self.reset()
        self.onlyRunningCopy()
        OMFIT['MainSettings'].sort()

    def projectName(self):
        if not len(self.filename):
            return ''
        if re.findall('OMFITsave.txt', self.filename):
            return os.path.split(self.filename.split(os.sep + 'OMFITsave.txt')[0])[1]
        else:
            return os.path.splitext(os.path.split(self.filename)[1])[0]

    def onlyRunningCopy(self, deletePID=False):
        """
        :param delete: whether to remove PID from list of running OMFIT processes (this should be done only at exit)

        :return: return True/False wether this is the only running copy of OMFIT on this computer
        """
        filename = os.sep.join([OMFITsessionsDir, str(os.getpid())])

        # OMFITsessionsDir should always exist! -- if not return False
        if not os.path.exists(OMFITsessionsDir):
            printe('Something is wrong! OMFITsessionsDir (%s) has been deleted!' % OMFITsessionsDir)
            return False
        else:
            try:
                # this is in a try/except because
                # in some extreme circumstances there can be
                # errors if the system cannot allocate memory
                if not os.path.exists(filename):
                    open(filename, 'w').close()
                pids = []
                for file in glob.glob(os.sep.join([OMFITsessionsDir, '*'])):
                    pid = os.path.split(file)[1]
                    if is_running(pid):
                        pids.append(pid)
                    elif deletePID:
                        try:
                            os.remove(file)
                        except OSError:
                            pass
                if deletePID and os.path.exists(filename):
                    os.remove(filename)
                return len(pids) == 1
            except OSError:
                return False

    def reset(self):
        # always use saving as .zip as the default
        self.zip = True

        # clear
        self.clear()
        OMFITconsoleDict.clear()
        OMFITscriptsDict.clear()

        # remove all files under current temporary directory
        try:
            shutil.rmtree(OMFITcwd)
        except Exception:
            pass
        if not os.path.exists(OMFITcwd):
            os.makedirs(OMFITcwd)
        os.chdir(OMFITcwd)

        # fill special locations
        super().__setitem__('scratch', OMFITmainscratch())
        super().__setitem__('commandBox', OMFITconsoleDict)
        super().__setitem__('scriptsRun', OMFITscriptsDict)
        super().__setitem__('shotBookmarks', OMFITshotBookmarks)

        # create main settings
        self.addMainSettings(restore='user')
        OMFIT['MainSettings']['EXPERIMENT']['runid'] = 'sim1'
        self['MainSettings']['SETUP']['version'] = repo_active_branch_commit
        self['MainSettings']['SETUP']['python_environment'] = SortedDict(python_environment())

        # initialize main scratch
        self['scratch'].initialize()

        # set the localhost
        SERVER.setLocalhost()

    def newProvenanceID(self):
        self['MainSettings']['EXPERIMENT']['provenanceID'] = omfit_hash(utils_base.now("%Y-%m-%d_%H_%M_%S_%f"))

    def newProjectID(self):
        self['MainSettings']['EXPERIMENT']['projectID'] = 'projectID__'
        self['MainSettings']['EXPERIMENT']['projectID'] += repo_active_branch_commit + '__'
        self['MainSettings']['EXPERIMENT']['projectID'] += utils_base.now("%Y-%m-%d_%H_%M_%S_%f")
        self['MainSettings']['EXPERIMENT']['projectID'] = self['MainSettings']['EXPERIMENT']['projectID'].replace(' ', '')

    def addMainSettings(self, updateUserSettings=False, restore=''):
        # read the user namelist file
        self.userMainSettings = OMFITsettingsDir + os.sep + 'MainSettings.txt'
        self.userMainSettingsNamelistDump = OMFITsettingsDir + os.sep + 'MainSettingsNamelistDump.txt'
        self.userMainSettingsNamelist = OMFITsettingsDir + os.sep + 'MainSettingsNamelist.txt'
        if not os.path.exists(os.path.split(self.userMainSettings)[0]):
            os.makedirs(os.path.split(self.userMainSettings)[0])
        if not os.path.exists(self.userMainSettings):
            open(self.userMainSettings, 'w').close()
            updateUserSettings = True
        if not os.path.exists(self.userMainSettingsNamelist):
            open(self.userMainSettingsNamelist, 'w').close()
            updateUserSettings = True

        # keep project options
        for k in list(OMFIT.prj_options_choices.keys()):
            if k not in self.prj_options:
                if k == 'persistent_projectID':
                    self.prj_options[k] = False
                else:
                    self.prj_options[k] = ''

        # force restore of skel main settings if necessary
        self.apply_bindings()
        if 'MainSettings' not in self or restore != '':
            # skeleton settings
            skelMainSettings = OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'skeleton' + os.sep + 'skeletonMainSettings.txt'
            self.tmpSkel = OMFITtree(skelMainSettings, quiet=True)
            if platform.system() == 'Darwin':
                skelMainSettings = (
                    OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'skeleton' + os.sep + 'skeletonMainSettingsNamelistOSX.txt'
                )
            else:
                skelMainSettings = (
                    OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'skeleton' + os.sep + 'skeletonMainSettingsNamelistUNIX.txt'
                )
            self.tmpSkel['MainSettings'].recursiveUpdate(namelist.NamelistFile(skelMainSettings), overwrite=True)

            # institution settings
            filename = os.sep.join([OMFITsrc, '..', 'institution'])
            if os.path.exists(filename):
                tmp = namelist.NamelistFile(filename)
            else:
                institution_files = glob.glob(os.sep.join([OMFITsrc, '..', 'institutions', '']) + '*')
                institution_files.append(None)
                for filename in institution_files:
                    tmp = namelist.NamelistFile(filename)
                    if 'SETUP' in tmp and 'stats_file' in tmp['SETUP'] and os.path.exists(tmp['SETUP']['stats_file']):
                        break
            self.tmpSkel['MainSettings'].recursiveUpdate(tmp, overwrite=True)

            # user settings
            self.tmpUser = OMFITtree(self.userMainSettings, quiet=True)
            if 'MainSettings' not in self:
                self['MainSettings'] = OMFITmainSettings()
            self['MainSettings'].filename = OMFITcwd + os.sep + os.path.split(self.userMainSettingsNamelist)[1]
            if not len(self.tmpUser):
                restore = 'skel'
                updateUserSettings = True

        # The main settings are built starting from the skeleton, the user local preference in ~/.OMFIT/ and the edits that the users have made
        if restore == '':
            self['MainSettings'].recursiveUpdate(self.tmpSkel['MainSettings'])

            def f_traverse(me):
                for kid in list(me.keys()):
                    if isinstance(me[kid], dict):
                        f_traverse(me[kid])
                    if re.match(hide_ptrn, kid):
                        del me[kid]

            f_traverse(self['MainSettings'])
            self.add_bindings_to_main_settings()

        elif restore.startswith('diff_'):
            restore = restore[5:]
            tmp = OMFITmainSettings()
            if restore == 'skel':
                tmp.recursiveUpdate(self.tmpSkel['MainSettings'])
            elif restore == 'user' and 'MainSettings' in self.tmpUser:
                tmp.recursiveUpdate(self.tmpSkel['MainSettings'])
                tmp.recursiveUpdate(self.tmpUser['MainSettings'], overwrite=True)
            elif restore == 'S3':
                tmp.recursiveUpdate(self.tmpSkel['MainSettings'])
                tmp.recursiveUpdate(self.tmpUser['MainSettings'], overwrite=True)
                tmp1 = OMFITobject_fromS3(tmp['SETUP']['email'] + "_" + 'MainSettings.txt', s3bucket='omfit')
                tmp2 = OMFITobject_fromS3(tmp['SETUP']['email'] + "_" + 'MainSettingsNamelist.txt', s3bucket='omfit')
                shutil.copy2(tmp2.filename, os.path.split(tmp1.filename)[0] + os.sep + os.path.split(tmp2.filename)[1])
                tmp0 = OMFITtree(tmp1.filename, quiet=True)
                tmp.recursiveUpdate(tmp0['MainSettings'], overwrite=True)
                printi('Loaded MainSettings from the cloud')
            diffTreeGUI(OMFIT['MainSettings'], tmp)

        else:
            self['MainSettings'].clear()
            if restore == 'skel':
                self['MainSettings'].recursiveUpdate(self.tmpSkel['MainSettings'])
            elif restore == 'user' and 'MainSettings' in self.tmpUser:
                self['MainSettings'].recursiveUpdate(self.tmpSkel['MainSettings'])
                self['MainSettings'].recursiveUpdate(self.tmpUser['MainSettings'], overwrite=True)
            elif restore == 'S3':
                self['MainSettings'].recursiveUpdate(self.tmpSkel['MainSettings'])
                self['MainSettings'].recursiveUpdate(self.tmpUser['MainSettings'], overwrite=True)
                tmp1 = OMFITobject_fromS3(self['MainSettings']['SETUP']['email'] + "_" + 'MainSettings.txt', s3bucket='omfit')
                tmp2 = OMFITobject_fromS3(self['MainSettings']['SETUP']['email'] + "_" + 'MainSettingsNamelist.txt', s3bucket='omfit')
                shutil.copy2(tmp2.filename, os.path.split(tmp1.filename)[0] + os.sep + os.path.split(tmp2.filename)[1])
                tmp = OMFITtree(tmp1.filename, quiet=True)
                self['MainSettings'].recursiveUpdate(tmp['MainSettings'], overwrite=True)
                printi('Restored MainSettings from the cloud')
            self.apply_bindings()

        # generate unique projectID if that's not already there
        if 'projectID' not in self['MainSettings']['EXPERIMENT']:
            self.newProjectID()

        # generate unique provenanceID if that's not already there
        if 'provenanceID' not in self['MainSettings']['EXPERIMENT']:
            self.newProvenanceID()

        # make sure auto-save is not more often than 15 minutes
        try:
            self['MainSettings']['SETUP']['autosave_minutes'] = int(self['MainSettings']['SETUP']['autosave_minutes'])
            if self['MainSettings']['SETUP']['autosave_minutes'] < 15:
                raise OMFITexception('Auto-save time must be >= than 15 minutes')
        except Exception as _excp:
            printe('Error in setting Auto-save time\n' + repr(_excp))
            self['MainSettings']['SETUP']['autosave_minutes'] = 15

        # if default_tunnel is None, then set it based on what servers the user has access
        if self['MainSettings']['SERVER']['default_tunnel'] is None:
            favorite_tunnels = ['cybele', 'portal', 'cmodws', 'shenma', 'itm_gateway', 'iter_login', 'cfetr']
            default_tunnel = 'cybele'
            if os.path.exists(os.environ['HOME'] + '/.ssh/known_hosts'):
                with open(os.environ['HOME'] + '/.ssh/known_hosts', 'r') as f:
                    lines = [_f for _f in f.read().strip().split('\n') if _f]
                known_tunnels = []
                for line in lines:
                    try:
                        for server in line.split()[0].split(','):
                            try:
                                SERVER[server]
                                if SERVER(server) in favorite_tunnels:
                                    known_tunnels.append(SERVER(server))
                            except Exception:
                                pass
                    except IndexError:
                        pass
                for tunnel in favorite_tunnels:
                    if tunnel in known_tunnels:
                        default_tunnel = tunnel
                        break
            self['MainSettings']['SERVER']['default_tunnel'] = default_tunnel

        if updateUserSettings:
            # find differences of current MainSettings with respect to skeleton
            tmpU = OMFITtree()
            tmpU['MainSettings'] = copy.deepcopy(OMFIT['MainSettings'])
            ptrn = self.tmpSkel.pretty_diff(tmpU)

            # do not store projectID, provenanceID, or runid
            for k in ['projectID', 'provenanceID', 'runid']:
                if k in list(ptrn['MainSettings']['EXPERIMENT'].keys()):
                    del ptrn['MainSettings']['EXPERIMENT'][k]

            # keep only differences
            tmpU = prune_mask(tmpU, ptrn)

            # remove entries that are deprecated
            _clearDeprecatedMainSettings(tmpU['MainSettings'])

            # remove entries that are not in the skeleton
            for item in list(tmpU['MainSettings'].keys()):
                if item in list(tmpU['MainSettings'].keys()) and item not in self.tmpSkel['MainSettings']:
                    del tmpU['MainSettings'][item]
                if item in list(tmpU['MainSettings'].keys()) and item != 'SERVER':
                    for subitem in list(tmpU['MainSettings'][item].keys()):
                        if (
                            subitem in list(tmpU['MainSettings'][item].keys())
                            and subitem not in self.tmpSkel['MainSettings'][item]
                            and subitem != 'KeyBindings'
                        ):
                            del tmpU['MainSettings'][item][subitem]
                        elif subitem == 'KeyBindings':
                            for desc, event in list(tmpU['MainSettings'][item][subitem].items()):
                                if (
                                    desc in global_event_bindings.default_desc_event
                                    and global_event_bindings.default_desc_event[desc] == event
                                ):
                                    del tmpU['MainSettings'][item][subitem][desc]

            # save only differences (if there are any)
            if len(tmpU):
                tmpU._save(filename=self.userMainSettings, only="['MainSettings']", onlyOMFITsave=True)
                global OMFITexpressionsReturnNone
                tmpExp = OMFITexpressionsReturnNone
                OMFITexpressionsReturnNone = True
                try:
                    tmpU['MainSettings'].saveas(self.userMainSettingsNamelist)
                finally:
                    OMFITexpressionsReturnNone = tmpExp
                self.tmpUser = tmpU
                printi(self.userMainSettings + ' has been updated')

            if updateUserSettings == 'S3':
                OMFITascii(OMFITsettingsDir + os.sep + 'MainSettings.txt').deploy(
                    self['MainSettings']['SETUP']['email'] + "_" + 'MainSettings.txt', s3bucket='omfit'
                )
                OMFITascii(OMFITsettingsDir + os.sep + 'MainSettingsNamelist.txt').deploy(
                    self['MainSettings']['SETUP']['email'] + "_" + 'MainSettingsNamelist.txt', s3bucket='omfit'
                )
                printi('Saved user MainSettings in the cloud')

        # save a version of MainSettings in plain text
        if updateUserSettings or not os.path.exists(self.userMainSettingsNamelistDump):
            self['MainSettings'].deploy(self.userMainSettingsNamelistDump)

    def __setitem__(self, key, value):
        # TODO: handle 'MainSettings' the same way
        if key in ['scratch', 'commandBox', 'scriptsRun', 'shotBookmarks']:
            raise RuntimeError(f"OMFIT['{key}'] is write-protected")
        else:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        if key in ['scratch', 'commandBox', 'scriptsRun', 'shotBookmarks', 'MainSettings']:
            raise RuntimeError(f"OMFIT['{key}'] is delete-protected")
        else:
            super().__delitem__(key)

    def add_bindings_to_main_settings(self):
        """
        Take the descriptions and events from global_events_bindings and insert
        them in self['MainSettings']['SETUP']['KeyBindings'][desc] = <event>
        """
        printd('Calling add_bindings_to_main_settings', level=2, topic='keybindings')
        if 'KeyBindings' not in self['MainSettings']['SETUP']:
            self['MainSettings']['SETUP']['KeyBindings'] = namelist.NamelistName()
        for di, d in enumerate(global_event_bindings.descs):
            self['MainSettings']['SETUP']['KeyBindings'][d.replace(' ', '_')] = global_event_bindings.events[di]

    def apply_bindings(self):
        """
        Take the descriptions and events from
        self['MainSettings']['SETUP']['KeyBindings']
        and use them to update the global_event_bindings
        """
        if ('MainSettings' not in self) or ('SETUP' not in self['MainSettings']) or ('KeyBindings' not in self['MainSettings']['SETUP']):
            printd("No key bindings in MainSettings['SETUP']['KeyBindings'] -> unable to update", topic='keybindings')
            return
        for d, e in list(self['MainSettings']['SETUP']['KeyBindings'].items()):
            try:
                global_event_bindings.set(d.replace('_', ' '), e)
            except ValueError:
                del self['MainSettings']['SETUP']['KeyBindings'][d]

        self.add_bindings_to_main_settings()

    def save(self, quiet=False, skip_save_errors=False):
        """
        Writes the content of the OMFIT tree to the filesystem
        using the same filename and zip options of the last saveas

        :param quiet: whether to print save progress to screen

        :param skip_save_errors: skip errors when saving objects
        """
        self.filename = self._save_with_info(self.filename, zip=self.zip, quiet=quiet, skip_save_errors=skip_save_errors)
        return self.filename

    def _save_with_info(self, filename, zip=False, quiet=False, updateExistingDir=False, skip_save_errors=False):
        """
        Wrapper function around the OMFITtree._save method which
        handles the prj_options dictionary that is only part of the main OMFIT tree
        """

        # this method should have the same signature of the ._save() method

        if filename:
            # by default the first time the projects directory is created,
            # assign permissions so that it is readeable but not writeable
            # by other users. Users can always override these default permissions
            # once the directory is created.
            projpath = os.path.split(os.path.split(filename)[0])[0]
            if not os.path.exists(projpath):
                # create projects directory
                os.makedirs(projpath)
                # by default, remove group and others write permission
                for perm in [stat.S_IWGRP, stat.S_IWOTH]:
                    st_mode = os.lstat(projpath).st_mode
                    os.chmod(projpath, st_mode & ~perm)
                # by default, add group and others read and browse permission
                for perm in [stat.S_IRGRP, stat.S_IROTH, stat.S_IXGRP, stat.S_IXOTH]:
                    st_mode = os.lstat(projpath).st_mode
                    os.chmod(projpath, st_mode | perm)

            # update list of shots/times from mainSettings and modules settings
            modules = self.moduleDict()
            for k in ['device', 'shot', 'time']:
                self.prj_options[k] = []
            for k in ['device', 'shot', 'shots', 'time', 'times']:
                self.prj_options[k.rstrip('s')].extend(tolist(evalExpr(self['MainSettings']['EXPERIMENT'][k])))
                try:
                    for module in list(modules.keys()):
                        mod = eval('OMFIT' + module)
                        self.prj_options.setdefault(k.rstrip('s'), []).extend(
                            tolist(evalExpr(mod['SETTINGS'].get('EXPERIMENT', {}).get(k, None)))
                        )
                    self.prj_options[k.rstrip('s')] = list([_f for _f in self.prj_options[k.rstrip('s')] if _f])
                except Exception as _excp:
                    printe('Error accessing `%s` of module `OMFIT%s` : %s' % (k, module, repr(_excp)))
            for k in ['device', 'shot', 'time']:
                self.prj_options[k] = np.unique(list([_f for _f in self.prj_options[k.rstrip('s')] if _f])).tolist()

            # if the GUI is open update the GUI elements info
            if OMFITaux['GUI']:
                commands = []
                commandNames = []
                for k in range(len(OMFITaux['GUI'].command)):
                    tmp = OMFITaux['GUI'].command[k].get(1.0, tk.END).strip()
                    if len(tmp):
                        commands.append(OMFITaux['GUI'].command[k].get(1.0, tk.END))
                        commandNames.append(OMFITaux['GUI'].commandNames[k])
                if not len(commands):
                    commands.append('')
                    commandNames.append('1')
                OMFIT.prj_options['commands'] = commands
                OMFIT.prj_options['commandNames'] = commandNames
                OMFIT.prj_options['namespace'] = OMFITaux['GUI'].commandBoxNamespace
                OMFIT.prj_options['notes'] = OMFITaux['GUI'].notes.get(1.0, tk.END).strip()
                OMFIT.prj_options['console'] = OMFITaux['console'].get()
                OMFIT.prj_options.setdefault('color', '')

                if OMFIT.prj_options['color'] not in list(OMFIT.prj_options_choices['color'].keys()):
                    OMFIT.prj_options['color'] = ''

                if OMFIT.prj_options['type'] not in OMFIT.prj_options_choices['type']:
                    OMFIT.prj_options['type'] = ''

            try:
                OMFITaux['hardLinks'] = True
                self['__GUISAVE__'] = self.prj_options
                cb = OMFITtree()
                for k, v in enumerate(self['__GUISAVE__']['commands']):
                    if not v.strip():
                        continue
                    try:
                        cb['%d.py' % (k + 1)] = OMFITascii(filename='%d.py' % (k + 1), fromString=v.rstrip())
                    except Exception as _excp:
                        printe(_excp)
                if list(cb.keys()):
                    self['__COMMANDBOX__'] = cb
                orig_version = self['MainSettings']['SETUP']['version']
                orig_environ = self['MainSettings']['SETUP']['python_environment']
                self['MainSettings']['SETUP']['version'] = repo_active_branch_commit
                self['MainSettings']['SETUP']['python_environment'] = SortedDict(python_environment())
                return self._save(
                    filename,
                    zip=zip,
                    quiet=quiet,
                    skipStorage=False,
                    updateExistingDir=updateExistingDir,
                    skip_save_errors=skip_save_errors,
                )

            except Exception:
                self['MainSettings']['SETUP']['version'] = orig_version
                self['MainSettings']['SETUP']['python_environment'] = orig_environ
                raise

            finally:
                if '__GUISAVE__' in self:
                    del self['__GUISAVE__']
                if '__COMMANDBOX__' in self:
                    del self['__COMMANDBOX__']
                OMFITaux['hardLinks'] = False

        else:
            raise IOError('Last saved directory was not defined')

    def saveas(self, filename, zip=None, quiet=False, skip_save_errors=False):
        """
        Writes the content of the OMFIT tree to the filesystem
        and permanently changes the name of the project

        :param filename: project filename to save to

        :param zip: whether the save should occur as a zip file

        :param quiet: whether to print save progress to screen

        :param skip_save_errors: skip errors when saving objects
        """
        oldZip = self.zip
        oldFilename = self.filename
        oldPrj_options = self.prj_options

        if zip is not None:
            self.zip = zip
        self.filename = filename

        try:
            return self.save(quiet=quiet, skip_save_errors=skip_save_errors)

        except Exception:
            self.zip = oldZip
            self.filename = oldFilename
            self.prj_options = oldPrj_options
            raise

    def loadModule(
        self,
        filename,
        location=None,
        withSubmodules=True,
        availableModulesList=None,
        checkLicense=True,
        developerMode=None,
        depth=0,
        quiet=False,
        startup_lib=None,
        **kw,
    ):
        r"""
        Load a module in OMFIT

        :param filename: * full path to the module to be loaded
                         * if just the module name is provided, this will be loaded from the public modules
                         * remote/branch:module format will load a module from a specific git remote and branch
                         * module:remote/branch format will load a module from a specific git remote and branch

        :param location: string with the location where to place the module in the OMFIT tree

        :param withSubmodules: load submodules or not

        :param availableModulesList: list of available modules generated by ``OMFIT.availableModules()``
                                     If this list is not passed, then the availableModulesList is generated internally

        :param checkLicense: Check license files at load

        :param developerMode: Load module with developer mode option (ie. scripts loaded as modifyOriginal)
                              if None then default behavior is set by ``OMFIT['MainSettings']['SETUP']['developer_mode_by_default']``
                              Note: public OMFIT installation cannot be loaded in developer mode

        :param depth: parameter used internally by for keeping track of the recursion depth

        :param quiet: load modules silently or not

        :param startup_lib: Used internally for executing OMFITlib_startup scripts

        :param \**kw: additional keywords passed to OMFITmodule() class

        :return: instance of the loaded module
        """
        if os.sep not in filename or ':' in filename:
            # if there is a semicolumn in the filename, then a specific remote/branch is been requested
            if ':' in filename:
                work_repo = repo.clone()
                remote, branch = [x for x in filename.split(':') if '/' in x][0].split('/')
                filename = [x for x in filename.split(':') if '/' not in x][0]
                work_repo.switch_branch(branch, remote)
                filename = os.sep.join([work_repo.git_dir, 'modules', filename, 'OMFITsave.txt'])
            else:
                # if it's just a module name, load it from the first of the OMFITmodule directories
                filename = os.sep.join([OMFITmodule.directories()[0], filename, 'OMFITsave.txt'])
        filename = os.path.abspath(filename)

        # get list of available modules
        if availableModulesList is None:
            availableModulesList = self.availableModules(quiet=True, same_path_as=filename)

        # handle developerMode switch
        OMFITsrc = os.path.split(os.path.split(os.path.split(filename)[0])[0])[0] + os.sep + 'omfit'
        if os.path.exists(os.sep.join([OMFITsrc, '..', 'public'])):
            developerMode = False
        if developerMode is None:
            developerMode = OMFIT['MainSettings']['SETUP']['developer_mode_by_default']

        # load the module
        moduleName = OMFITmodule.info(filename).get('ID', 'unknown_module')
        if location is None:
            location = "self['" + moduleName + "']"

        # handle printing
        kw.pop('quiet', None)
        quiet_module = True
        if not quiet:
            quiet_module = {
                'newline': False,
                'clean': False,
                'quiet': False,
                'style': ' [{sfill}{svoid}] {perc:3.2f}% ' + '*' * (depth + 1) + ' ' + moduleName + '{mess}',
            }

        # load module
        tmp = OMFITmodule(filename, developerMode=developerMode, quiet=quiet_module, **kw)
        # remove the module filename as there is no point of keeping it once it's loaded from the repo
        # OMFITtree (and derived classes) filenames are used for saving them external to the project
        tmp.filename = ''

        # if loading as a submodule, then place at the top
        loc = parseLocation(location)
        if isinstance(eval(buildLocation(loc[:-1])), OMFITmodule):
            eval(buildLocation(loc[:-1])).insert(0, loc[-1], tmp)
        else:
            eval(buildLocation(loc[:-1]))[loc[-1]] = tmp

        # add extra commit info to MODULE
        if filename in availableModulesList:
            for k in _moduleAttrs:
                if k in availableModulesList[filename]:
                    tmp['SETTINGS']['MODULE'][k] = availableModulesList[filename][k]

        # fill in missing infos (e.g. when starting a new module)
        if not tmp['SETTINGS']['MODULE']['commit']:
            tmp['SETTINGS']['MODULE']['commit'] = repo.get_hash('HEAD')
        if tmp['SETTINGS']['MODULE']['contact'] is None:
            tmp['SETTINGS']['MODULE']['contact'] = []
        if not len(tmp['SETTINGS']['MODULE']['contact']) and OMFIT['MainSettings']['SETUP']['email']:
            tmp['SETTINGS']['MODULE']['contact'].append(OMFIT['MainSettings']['SETUP']['email'])

        # Check license
        if checkLicense and 'license' in eval(location):
            license = eval(location)['license']
            email_dict = {}

            with open(license.filename, 'r') as f:
                for k in f.readlines():
                    k = str(k)
                    if 'OMFIT_license_email_notify' in k:
                        notify = [x.strip() for x in re.sub(r'OMFIT_license_email_notify\:(.*)', r'\1', k).strip().split(',')]
                        email_dict = {
                            'email_address': notify,
                            'email_prompt': 'Please describe planned research using ' + moduleName,
                            'fromm': self['MainSettings']['SETUP']['email'],
                        }
                        break

            try:
                OMFITlicenses[moduleName] = License(moduleName, license.filename, email_dict=email_dict, rootGUI=OMFITaux['rootGUI'])
                if OMFITaux['rootGUI']:
                    OMFITlicenses[moduleName].check()
            except LicenseException:
                exec('del ' + location, globals(), locals())
                raise
            except tk.TclError:  # If there is no DISPLAY, allow access
                pass
            except IndexError:  # If gui element fails to load, allow access
                pass

        # load the submodules (will set DEPENDENCIES, SETTINGS['EXPERIMENT'], and honor LIB['OMFITlib_startup'] scripts)
        if withSubmodules:
            # find the submodules (one level deep)
            moduleDict = eval(location).moduleDict(level=0)

            # save the dependencies
            depsDict = {}
            for subMod in moduleDict:
                depsDict[subMod] = eval(location + subMod)['SETTINGS']['DEPENDENCIES']

            # load the submodules
            if startup_lib is None:
                startup_lib = []
            for subMod in moduleDict:
                found = False
                for avMod in availableModulesList:
                    if moduleDict[subMod]['ID'] == availableModulesList[avMod]['ID']:
                        OMFIT.loadModule(
                            availableModulesList[avMod]['path'],
                            location + subMod,
                            withSubmodules=True,
                            availableModulesList=availableModulesList,
                            checkLicense=checkLicense,
                            developerMode=developerMode,
                            depth=depth + 1,
                            quiet=quiet,
                            startup_lib=startup_lib,
                            **kw,
                        )
                        found = True
                        break
                if not found:
                    raise IOError(
                        'Module %s is a submodule of %s, and it could not found in %s'
                        % (moduleDict[subMod]['ID'], moduleName, os.path.split(os.path.split(filename)[0])[0])
                    )

            # restore the dependencies
            for subMod in moduleDict:
                for avMod in availableModulesList:
                    if moduleDict[subMod]['ID'] == availableModulesList[avMod]['ID']:
                        eval(location + subMod)['SETTINGS']['DEPENDENCIES'].update(depsDict[subMod])
                        break

            # freeze the root['SETTINGS']['EXPERIMENT'] entries if this is a top-level import that is not a submodule
            if depth == 0 and 'SETTINGS' in eval(location) and 'EXPERIMENT' in eval(location)['SETTINGS']:
                freeze = True
                for tmpName in reversed(traverseLocation(location)[:-1]):
                    if eval(tmpName).__class__ is OMFITmodule and tmpName != 'OMFIT':
                        freeze = False
                if freeze:
                    for item in list(OMFITaux['moduleSkeletonCache']['SETTINGS']['EXPERIMENT'].keys()):
                        eval(location)['SETTINGS']['EXPERIMENT'][item] = evalExpr(eval(location)['SETTINGS']['EXPERIMENT'][item])

            # execute startup script (the OMFITmodulePath variable is setup to point to the OMFITsave.txt file of the module that is being loaded)
            if 'LIB' in eval(location) and 'OMFITlib_startup' in eval(location)['LIB']:
                startup_lib.append((moduleName, location, eval(location)['LIB']['OMFITlib_startup']))

            if depth == 0:
                for k, (mname, loc, st_lib) in enumerate(startup_lib):
                    if not quiet:
                        if k == 0:
                            printi("Running OMFITlib_startup:", end='')
                        printi(f' {mname}', end='')
                    try:
                        with quiet_environment():
                            st_lib.runNoGUI()
                    except Exception as _excp:
                        printe("Error in %s['LIB']['OMFITlib_startup'] : " % (loc) + repr(_excp))
                if not quiet:
                    printi('')

            # store settings at load time
            # NOTE: this is done both here and in OMFITmodule.__init__ because this one will get execution of OMFITlib_startup and the other instead is needed when reloading a module
            eval(location)._save_settings_at_import()

        # return the module
        return eval(location)

    def load(self, filename, persistent_projectID=False):
        """
        loads an OMFITproject in OMFIT

        :param filename: filename of the project to load (if `-1` then the most recent project is loaded)

        :param persistent_projectID: whether the projectID should remain the same
        """
        try:

            # open the last project
            if filename == '-1':
                projects = OMFIT.recentProjects()
                if len(projects):
                    filename = list(projects.keys())[0]
                    persistent_projectID = projects[filename].get('persistent_projectID', False)

            # keep aside user 'SETUP','SERVER'
            tmp = {}
            for item in ['SETUP', 'SERVER']:
                if item in self['MainSettings']:
                    tmp[item] = copy.deepcopy(self['MainSettings'][item])

            self.filename = os.path.abspath(filename)

            oldDir = os.getcwd()
            TMPnoCopyToCWD = OMFITaux['noCopyToCWD']
            OMFITaux['noCopyToCWD'] = False
            try:
                self._load(filename)
            finally:
                os.chdir(oldDir)
                OMFITaux['noCopyToCWD'] = TMPnoCopyToCWD

            if zipfile.is_zipfile(self.filename):
                self.zip = True
                projectName = os.path.split(self.filename)[1]
            else:
                self.zip = False
                projectName = os.path.split(os.path.split(self.filename)[0])[1]

            # for older projects we calculate provenanceID based on institution and projectName
            # very old projects do not even have institution info
            if 'provenanceID' not in self['MainSettings']['EXPERIMENT']:
                self['MainSettings']['EXPERIMENT']['provenanceID'] = omfit_hash(
                    self['MainSettings']['SETUP'].get('institution', 'old_project') + '_' + projectName
                )

            # SETUP is overwritten (but not version nor python_environment)
            project_version = self['MainSettings']['SETUP'].get('version', '?')
            project_environ = self['MainSettings']['SETUP'].get('python_environment', {})
            self['MainSettings']['SETUP'] = tmp['SETUP']
            self['MainSettings']['SETUP']['version'] = project_version
            self['MainSettings']['SETUP']['python_environment'] = project_environ

            # SERVER is updated
            self['MainSettings'].setdefault('SERVER', NamelistName()).update(tmp.get('SERVER', {}))

            # load project options
            self.prj_options.clear()
            tmp = OMFITproject.info(self.filename)
            for k in OMFIT.prj_options_choices:
                self.prj_options[k] = tmp.get(k, '')
            for whereSave in ['__GUISAVE__', '__COMMANDBOX__']:
                if whereSave in OMFIT:
                    del OMFIT[whereSave]
            if self.prj_options['color'] not in list(self.prj_options_choices['color'].keys()):
                self.prj_options['color'] = ''
            if self.prj_options['type'] not in self.prj_options_choices['type']:
                self.prj_options['type'] = ''
            if 'namespace' not in self.prj_options or not self.prj_options['namespace']:
                self.prj_options['namespace'] = 'OMFIT'

            # update projectID
            self.prj_options['persistent_projectID'] = persistent_projectID
            if not persistent_projectID:
                self.newProjectID()

            # keep MainSettings in check
            self.updateMainSettings()
            self['MainSettings'].sort()

            # set the localhost
            SERVER.setLocalhost()

            # remote projects are loaded in OMFITtmpDir
            # reset the filename to force users to decide how/where to save it
            if OMFITtmpDir in self.filename:
                self.filename = ''

        except Exception:
            self.start()
            raise

    def updateCWD(self):
        global OMFITcwd
        self._save(filename=OMFITcwd + os.sep + 'OMFITsave.txt', skipStorage=False)

    def updateMainSettings(self):
        self.addMainSettings()
        self.keyOrder.remove('scratch')
        self.keyOrder.append('scratch')
        self.keyOrder.remove('commandBox')
        self.keyOrder.append('commandBox')
        self.keyOrder.remove('scriptsRun')
        self.keyOrder.append('scriptsRun')
        self.keyOrder.remove('shotBookmarks')
        self.keyOrder.append('shotBookmarks')
        self.keyOrder.remove('MainSettings')
        self.keyOrder.append('MainSettings')

    def saveMainSettingsSkeleton(self):
        """
        This utility function updates the MainSettingsSkeleton for the current OMFIT installation
        """
        self['MainSettings'].sort()
        tmp = copy.deepcopy(self['MainSettings'])
        self.addMainSettings(restore='skel')
        keys = self['MainSettings'].keys()
        for k in keys:
            if k.startswith('__comment'):
                del self['MainSettings'][k]
        self['MainSettings'].sort()

        try:
            self['MainSettings'].filename = self['MainSettings']['SETUP']['workDir'] + '../' + 'skeletonMainSettingsNamelist.txt'

            self['MainSettings']['SETUP']['version'] = '?'
            self['MainSettings']['SETUP']['python_environment'] = {}
            del self['MainSettings']['EXPERIMENT']['projectID']
            del self['MainSettings']['EXPERIMENT']['provenanceID']

            self['MainSettings']['SETUP']['browser'] = None
            self['MainSettings']['SETUP']['Extensions'].clear()

            # Avoid changes made by institution file
            self['MainSettings']['SETUP']['stats_file'] = OMFITexpression("os.path.abspath(OMFITsettingsDir+'/OMFITstats.txt')")
            self['MainSettings']['SETUP']['institution'] = 'PERSONAL'
            if 'institutionProjectsDir' in self['MainSettings']['SETUP']:
                del self['MainSettings']['SETUP']['institutionProjectsDir']
            self['MainSettings']['EXPERIMENT']['device'] = None

            for k in tmp['SERVER']:
                if k not in self['MainSettings']['SERVER']:
                    self['MainSettings']['SERVER'][k] = tmp['SERVER'][k]
                if isinstance(tmp['SERVER'][k], namelist.NamelistName):
                    self['MainSettings']['SERVER'][k].update(tmp['SERVER'][k])

            self['MainSettings']['SERVER']['localhost'] = namelist.NamelistName()
            self['MainSettings']['SERVER']['localhost']['workDir'] = OMFITexpression("OMFITcwd+os.sep+'remote_runs'+os.sep")
            self['MainSettings']['SERVER']['localhost']['server'] = 'localhost'
            self['MainSettings']['SERVER']['localhost']['tunnel'] = ''
            self['MainSettings']['SERVER']['localhost']['idl'] = ''
            self['MainSettings']['SERVER']['localhost']['matlab'] = ''

            self['MainSettings']['SERVER']['default_tunnel'] = None

        finally:
            self['MainSettings'].sort()
            self._save(
                filename=OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'skeleton' + os.sep + 'skeletonMainSettings.txt',
                only="['MainSettings']",
                updateExistingDir=True,
            )
            self['MainSettings'] = tmp

    def availableModules(self=None, quiet=None, directories=None, same_path_as=None, force=False):
        """
        Index available OMFIT modules in directories

        :param quiet: verbosity

        :param directories: list of directories to index. If `None` this is taken from OMFIT['MainSettings']['SETUP']['modulesDir']

        :param same_path_as: sample OMFITsave.txt path to set directory to index

        :param force: force rebuild of .modulesInfoCache file

        :return: This method returns a dictionary with the available OMFIT modules.
                 Each element in the dictionary is a dictionary itself with the details of the available modules.
        """
        if directories is None:
            directories = OMFITmodule.directories()
        else:
            directories = tolist(directories)

        if same_path_as is None:
            pass
        elif 'OMFITsave.txt' in same_path_as and os.path.exists(same_path_as):
            directories = [os.path.split(os.path.split(same_path_as)[0])[0]]
        else:
            raise IOError('%s file is not a valid OMFITsave.txt file' % same_path_as)

        updatePersistentCache = []
        moduleDict = {}
        for directory in directories:  # the user inputs the directory where the modules are
            if not quiet:
                tmp = 'Modules directory: ' + directory
                printi('=' * len(tmp))
                printi(tmp)
                printi('=' * len(tmp))
                print('', end='')

            if not force and os.path.exists(directory + os.sep + '.modulesInfoCache'):
                try:
                    with open(directory + os.sep + '.modulesInfoCache', 'rb') as f:
                        _availableModulesCache[directory] = pickle.load(f)
                except Exception:
                    _availableModulesCache[directory] = {}
                    printw('-- Failed to load persistent git modules cache --')
            else:
                _availableModulesCache[directory] = {}

            # modules in directory
            modules_list_in_dir = sorted(
                [os.path.abspath(x) for x in glob.glob(os.sep.join([directory, '*', 'OMFITsave.txt']))], key=lambda x: x.lower()
            )

            # try handling git repository of modules twice
            # first as if git root directory parent directory of modules directory
            # second as if git root directory is modules directory
            cases_errors = []
            cases = []
            if os.path.split(directory)[1] == 'modules':
                cases.append([os.path.split(directory)[0], 'modules'])
            cases.append([directory, ''])

            for repo_dir, modules_subpath in cases:
                try:
                    # try to access as a git repository
                    repo = OMFITgit(repo_dir)
                    commit = repo("log -1 --pretty='%H'")
                    branch = repo('rev-parse --abbrev-ref HEAD')
                    remote = repo.get_branches().get(branch, {'remote': ''})['remote']

                    changed_modules = []

                    # if same remote/branch and commit
                    if (
                        np.all([k in _availableModulesCache[directory] for k in ['branch', 'remote', commit]])
                        and _availableModulesCache[directory]['remote'] == remote
                        and _availableModulesCache[directory]['branch'] == branch
                    ):
                        changes = list([_f for _f in repo("ls-files -m --others --exclude-standard " + directory).split('\n') if _f])
                        for mod_path in modules_list_in_dir:
                            if (
                                mod_path not in _availableModulesCache[directory][commit]
                                or len(_availableModulesCache[directory][commit][mod_path]['modified'])
                                or len(_availableModulesCache[directory][commit][mod_path]['untracked'])
                            ):
                                changes.append(os.sep.join(mod_path.split(os.sep)[[-2, -3][len(modules_subpath) > 0] :]))

                        if len(changes):
                            if not quiet:
                                printi('-- some modules changes are not part of git --')
                            for mod in tolist(np.unique([x.split(os.sep)[[0, 1][len(modules_subpath) > 0]] for x in changes])):
                                mod_path = directory + os.sep + mod
                                if not os.path.exists(mod_path):
                                    raise Exception(mod_path + ' does not exist')
                                tmp = repo.get_module_params(quiet=quiet, path=modules_subpath, key='path', modules=[mod_path])
                                _availableModulesCache[directory][commit].update(tmp)
                                changed_modules.append(os.path.abspath(mod_path + os.sep + 'OMFITsave.txt'))
                        elif not quiet:
                            printi('-- modules cache is valid --')
                    else:
                        # if same remote/branch then try to update since recorded commit (faster: only need to loop over modules that changed)
                        if (
                            np.all([k in _availableModulesCache[directory] for k in ['branch', 'remote']])
                            and len(_availableModulesCache[directory]) == 3
                            and _availableModulesCache[directory]['remote'] == remote
                            and _availableModulesCache[directory]['branch'] == branch
                        ):
                            printi('-- updating modules cache since last commit --')
                            try:
                                old_commit = [
                                    item for item in list(_availableModulesCache[directory].keys()) if item not in ['branch', 'remote']
                                ][0]
                                changes = np.unique(
                                    [
                                        modules_subpath + '/' + re.sub('^' + modules_subpath + '/', '', x).split(os.sep)[0]
                                        for x in repo('diff --name-only %s %s -- %s' % (old_commit, commit, modules_subpath)).split()
                                    ]
                                ).tolist()
                                changed_modules = [os.sep.join([repo_dir, x, 'OMFITsave.txt']) for x in changes]
                                _availableModulesCache[directory][commit] = _availableModulesCache[directory][old_commit]
                                del _availableModulesCache[directory][old_commit]
                                _availableModulesCache[directory][commit].update(
                                    repo.get_module_params(quiet=quiet, path=modules_subpath, key='path', modules=changed_modules)
                                )
                            except Exception as _excp:
                                printw('Failed to update available modules cache: ' + repr(_excp))
                                del _availableModulesCache[directory]
                        else:
                            printi('-- rebuilding modules cache from scratch --')
                            if directory in _availableModulesCache:
                                del _availableModulesCache[directory]
                        # if directory is not in _availableModulesCache then must build everything from scratch
                        if directory not in _availableModulesCache:
                            _availableModulesCache[directory] = {}
                            _availableModulesCache[directory]['branch'] = branch
                            _availableModulesCache[directory]['remote'] = remote
                            _availableModulesCache[directory][commit] = repo.get_module_params(
                                quiet=quiet, path=modules_subpath, key='path'
                            )
                        updatePersistentCache.append(directory)

                    # delete modules from cache if these are not found on hard drive
                    for mod_path in list(_availableModulesCache[directory][commit].keys()):
                        if not os.path.exists(_availableModulesCache[directory][commit][mod_path]['path']):
                            del _availableModulesCache[directory][commit][mod_path]

                    # update list of modules
                    moduleDict.update(_availableModulesCache[directory][commit])

                    # do not try 2nd case if 1st one worked
                    break

                except Exception as _excp:
                    cases_errors.append(_excp)
                    if len(cases_errors) == len(cases):

                        _availableModulesCache[directory].clear()

                        # if the path is not a valid git repository or the data was modified then get modules by hand
                        for mod_path in modules_list_in_dir:
                            if mod_path in moduleDict:
                                continue

                            mod = os.path.split(mod_path)[0]
                            mod_name = os.path.split(mod)[1]

                            if not quiet:
                                printi(mod_name.ljust(20) + ' (untracked)')

                            moduleDict[mod_path] = {}
                            moduleDict[mod_path]['path'] = mod_path
                            moduleDict[mod_path]['untracked'] = mod_path  # just for compatibility with data returned by `get_module_params`
                            moduleDict[mod_path]['modified'] = mod_path  # just for compatibility with data returned by `get_module_params`
                            moduleDict[mod_path]['edited_by'] = os.environ['USER']
                            moduleDict[mod_path]['date'] = convertDateFormat(time.time())
                            moduleDict[mod_path]['commit'] = ''
                            moduleDict[mod_path]['description'] = ''

                            info = OMFITmodule.info(moduleDict[mod_path]['path'])
                            info.pop('date', None)
                            info.pop('edited_by', None)
                            info.pop('commit', None)
                            moduleDict[mod_path].update(info)

            # save modules info cache
            if directory in updatePersistentCache or not os.path.exists(directory + os.sep + '.modulesInfoCache'):
                try:
                    with open(directory + os.sep + '.modulesInfoCache', 'wb') as f:
                        pickle.dump(_availableModulesCache[directory], f, pickle.OMFIT_PROTOCOL)
                    printi('-- Updated persistent git modules cache --')
                except IOError:
                    pass

        return moduleDict

    def quit(self, deepClean=False):
        """
        Cleanup current OMFIT session directory `OMFITsessionDir` and PID from `OMFITsessionsDir`
        Also close all SSH related tunnels and connections

        :param deepClean: if deepClean is True, then the `OMFITtmpDir` and `OMFITsessionsDir` get deleted
        """
        if OMFITcwd is None:
            return

        onlyRunningCopy = OMFIT.onlyRunningCopy(deletePID=True)

        if onlyRunningCopy:
            OMFIT.reset_connections()  # reset_connections() will also close_mds_connections()
        else:
            omfit_classes.omfit_mds.close_mds_connections()

        try:
            if os.path.exists(OMFITsessionDir):
                shutil.rmtree(OMFITsessionDir)
        except Exception:
            printw('Some files and directories could not be deleted!')

        if deepClean:
            if os.path.exists(OMFITsessionsDir):
                try:
                    shutil.rmtree(OMFITsessionsDir)
                    os.makedirs(OMFITsessionsDir)
                except OSError:
                    printw('Some files and directories under %s could not be deleted!' % OMFITsessionsDir)
            if os.path.exists(OMFITtmpDir):
                try:
                    shutil.rmtree(OMFITtmpDir)
                except Exception:
                    printw('Some files and directories under %s could not be deleted!' % OMFITtmpDir)

        return onlyRunningCopy

    def reset_connections(self, server=None, mds_cache=True):
        """
        Reset connections, stored passwords, and MDS+ cache

        :param server: only reset SSH connections to this server
        """
        import utils_widgets

        serverPicker = ''
        if server is None:
            printi('Reset OMFIT stored passwords')
            utils_widgets.stored_passwords.clear()

            if mds_cache:
                printi('Purge OMFIT MDS+ cache')
                OMFITmdsCache().purge()
            else:
                printi('OMFIT MDS+ cache not purged; use OMFITmdsCache().purge() to purge it')

            printi('Reset OMFIT SSH  connections')
            printi('Reset OMFIT MDS+ connections')
            omfit_classes.omfit_mds.close_mds_connections()
            printi('Reset OMFIT SQL  connections')
            for k in ['MDSserverReachable', 'RDBserverReachable', 'batch_js', 'sshTunnel', 'sysinfo']:
                OMFITaux[k] = copy.deepcopy(OMFITaux.defaults[k])

        else:
            if server:
                serverPicker = parse_server(SERVER[server]['server'])[2]
            printi('Reset OMFIT SSH  connections to %s' % serverPicker)

        sshServices = ['OMFITssh', 'OMFITsshTunnel', 'OMFITsshControlmaster', 'OMFITsshGit']

        # Have to create tmpdir since OMFIT tmp directory may have been cleaned up already
        import tempfile, shutil

        tmpdir = tempfile.mkdtemp()
        s = subprocess.Popen("ps xw", stdout=subprocess.PIPE, shell=True, cwd=tmpdir)
        std_out, std_err = s.communicate()
        shutil.rmtree(tmpdir)
        for item in b2s(std_out).split('\n'):
            service = [s for s in sshServices if re.search(s, item)]
            if len(service) and re.search(serverPicker, item):
                pid = int([_f for _f in item.split(' ') if _f][0])
                try:
                    printi('kill %s' % (item))
                    os.kill(int(pid), signal.SIGKILL)
                except OSError as e:
                    printw('Failed! %s' % repr(e))

    def recentProjects(self, only_read=False):
        """
        This routine keeps track of the recent projects
        and is also in charge of deleting auto-saves if they do not appear in the project list.

        :param read_only: only read projects file (don't do any maintenance on it)
        """

        # do not log projects that are in OMFITtmpDir
        if OMFITtmpDir in OMFIT.filename:
            return

        filename_old = OMFITsettingsDir + os.sep + 'OMFITrecentProjects.txt'
        filename = OMFITsettingsDir + os.sep + 'OMFITprojects.txt'
        autoSaveLinkDir = os.path.abspath(OMFIT['MainSettings']['SETUP']['projectsDir'].rstrip('/\\')) + os.sep + 'auto-save' + os.sep

        if not os.path.exists(filename) and os.path.exists(filename_old):
            shutil.copyfile(filename_old, filename)

        # read the projects
        projects = SortedDict()
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                lines = f.readlines()
            for k, line in enumerate(lines):
                line = line.strip()
                tmp = line.split('{')
                if len(tmp) == 1:
                    path = tmp[0].strip()
                    opts = {}
                else:
                    path = tmp[0].strip()
                    opts = eval('{' + '{'.join(tmp[1:]))
                if os.path.exists(path):
                    projects[path] = opts

        # add extra info (eg. file size)
        for item in list(projects.keys()):
            if 'size' not in projects[item] and os.path.exists(item) and item.endswith('.zip') and zipfile.is_zipfile(item):
                projects[item]['size'] = os.stat(item).st_size

        if only_read:
            return projects

        # this switch will be set to True if the recent projects file needs to be updated
        doWrite = False

        # delete `Self-Destruct` projects that have not been accessed in more than 30 days
        for item in list(projects.keys()):
            if projects[item].get('type', '') == 'Self-Destruct' and os.stat(item).st_atime < (time.time() - 30 * 86400):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                del projects[item]
                doWrite = True

        # add projects which for some reason were not already there at the bottom of the list
        if os.path.exists(os.path.abspath(evalExpr(OMFIT['MainSettings']['SETUP']['projectsDir']))):
            for item in glob.glob(os.path.abspath(evalExpr(OMFIT['MainSettings']['SETUP']['projectsDir'])) + os.sep + '*'):
                if os.path.isdir(item):
                    if os.path.exists(item + os.sep + 'OMFITsave.txt'):
                        item = item + os.sep + 'OMFITsave.txt'
                    else:
                        continue
                if item not in projects:
                    projects[item] = {}
                    doWrite = True

        # try to read prj_options for the projects which do not have them
        for item in list(projects.keys()):
            if 'device' not in projects[item]:
                try:
                    tmp = OMFITproject.info(item)
                except Exception as _excp:
                    printe('%s looks like an invalid OMFIT project' % (item))
                    del projects[item]
                    continue
                tmp.setdefault('notes', '')
                for opt in OMFIT.prj_options_choices:
                    if opt in tmp:
                        projects[item][opt] = tmp[opt]
                        doWrite = True

        # if the current project has been saved put it at the top of the list
        if (
            OMFIT.filename is not None
            and len(OMFIT.filename)
            and autoSaveLinkDir not in OMFIT.filename
            and OMFITautosaveDir not in OMFIT.filename
        ):
            item = os.path.abspath(OMFIT.filename)
            if item in list(projects.keys()):
                del projects[item]
            projects.insert(0, item, copy.deepcopy(OMFIT.prj_options))
            if item.endswith('.zip') and zipfile.is_zipfile(item):
                projects[item]['size'] = os.stat(item).st_size
            elif item.endswith('OMFITsave.txt'):
                projects[item]['size'] = size_of_dir(os.path.split(item)[0])
            doWrite = True

        # do not store console output, commands, and namespace in OMFITprojects.txt
        for item in list(projects.keys()):
            for opt in ['console', 'commands', 'namespace']:
                if opt in projects[item]:
                    del projects[item][opt]
                    doWrite = True

        # only store modules locations
        for item in list(projects.keys()):
            if isinstance(projects[item]['modules'], dict):
                projects[item]['modules'] = list(projects[item]['modules'].keys())

        # write OMFITprojects.txt~ then move to OMFITprojects.txt if successful
        # this is to have as much of an atomic operation as possible
        if doWrite:
            with open(filename_old + '~', 'w') as f_old, open(filename + '~', 'w') as f:
                for item in list(projects.keys()):
                    f.write('%s %s\n' % (item, projects[item]))
                    f_old.write('%s\n' % (item))
            shutil.move(filename + '~', filename)
            shutil.move(filename_old + '~', filename_old)

        # delete auto-saves that are older than one week
        # process one old auto-save at the time ones that were accessed first (deleting large auto-saves can take some time)
        for dir in [OMFITautosaveDir, autoSaveLinkDir]:
            # sort auto-saves by time
            files = glob.glob(dir + os.sep + '*')
            # delete broken links (otherwise getatime will fail)
            remove = []
            for path in files:
                if os.path.islink(path) and not os.path.exists(path):
                    os.remove(path)
                    remove.append(path)
            files = list(set(files).difference(set(remove)))
            # sort files
            files.sort(key=lambda x: os.path.getatime(x))
            for path in files:
                # delete auto-saves that have not been accessed in more than one week
                if not os.path.islink(path) and os.path.isdir(path) and os.stat(path).st_atime < (time.time() - 7 * 86400):
                    shutil.rmtree(path)
                    break  # delete one old auto-save at the time
                # delete broken links
                if os.path.islink(path) and not os.path.exists(path):
                    os.remove(path)

        return projects


class OMFITmainscratch(OMFITtmp):
    def __init__(self):
        self.required = list(map(lambda x: os.path.splitext(os.path.basename(x))[0], glob.glob(OMFITsrc + '/framework_guis/*.py')))

    def initialize(self):
        for item in self.required:
            self.load_framework_gui(item)

    def load_framework_gui(self, item):
        dev_acceptable = os.access(OMFITsrc + os.sep + 'framework_guis' + os.sep + item + '.py', os.W_OK) and not os.path.exists(
            os.sep.join([OMFITsrc, '..', 'public'])
        )
        self[f'__{item}__'] = OMFITpythonGUI(
            OMFITsrc + os.sep + 'framework_guis' + os.sep + item + '.py',
            modifyOriginal=OMFIT['MainSettings']['SETUP']['developer_mode_by_default'] & dev_acceptable,
        )

    def __delitem__(self, key):
        if key in self.required:
            self.load_framework_gui(key)
        else:
            super().__delitem__(key)


# --------------------------------
# Setup the global variable OMFIT
# --------------------------------
OMFIT.__class__ = OMFITmaintree  # root of the OMFIT tree
OMFIT.modifyOriginal = False
OMFIT.readOnly = False
OMFIT._OMFITkeyName = 'OMFIT'
OMFIT.prj_options = {}
OMFIT.prj_options_choices = {
    'notes': '',
    'commands': '',
    'commandNames': [],
    'namespace': '',
    'console': '',
    'shot': '',
    'time': '',
    'device': '',
    'modules': '',
    'type': ['Self-Destruct', 'Test', 'Working', 'Done', 'VIP'],
    'persistent_projectID': False,
    'color': OrderedDict(
        (
            ('red', 'red2'),
            ('orange', 'dark orange'),
            ('yellow', 'orange'),
            ('green', 'forest green'),
            ('blue', 'mediumblue'),
            ('purple', 'medium orchid'),
            ('gray', 'gray25'),
        )
    ),
}
atexit.register(OMFIT.quit)  # Register final automatic cleanup

# ------------------------------------
# location from root requires knowing what `OMFIT` is
# ------------------------------------
def locationFromRoot(location):
    """
    :param location: tree location

    :return: tree location from the closest root
    """
    tmp = location
    location = parseBuildLocation(location)
    for k in 1 + np.array(list(range(len(location) - 1))):
        loc = eval('OMFIT' + parseBuildLocation(location[:k]))
        if loc.__class__ is OMFITmodule:
            tmp = "root" + parseBuildLocation(location[k:])
    return tmp


def rootLocation(location, *args, **kw):
    """
    :param location: tree location

    :return: tree location of the root
    """
    if len(args) >= 1:
        OMFIT = args[0]
    if len(args) >= 2:
        kw['rootName'] = args[1]
    rootName = kw.setdefault('rootName', 'OMFIT')

    location = parseBuildLocation(location)
    root = 'OMFIT'
    for k in 1 + np.array(list(range(len(location) - 1))):
        loc = eval('OMFIT' + parseBuildLocation(location[:k]))
        if loc.__class__ is OMFITmodule:
            root = 'OMFIT' + parseBuildLocation(location[:k])
    root = rootName + root[5:]
    return root


# ---------------------
# Import OMFIT APIs
# and make it available to users Python scripts and expressions
# ---------------------
from omfit_classes import OMFITx

setattr(omfit_classes.omfit_python, 'OMFITx', OMFITx)
setattr(omfit_classes.omfit_base, 'OMFITx', OMFITx)

# ---------------------
# graphics
# ---------------------
from omfit_plot import *

# ---------------------
# update classes
# ---------------------
omfit_classes.omfit_base._updateTypes()

# ---------------------
# S3
# ---------------------
def OMFITobject_fromS3(filename, s3bucket):
    """
    Recovers OMFITobject from S3 and reloads it with the right class and original keyword parameters

    :return: object loaded from S3
    """
    s3connection = boto3.resource('s3', **boto_credentials())
    obj = s3connection.Object(s3bucket, filename)
    cls = eval(eval(obj.metadata.get('__class__', "'OMFITobject'")))
    orig_filename = eval(obj.metadata.get('__filename__', filename))
    tmp = cls(filename, s3bucket=s3bucket, **{k: eval(obj.metadata[k]) for k in obj.metadata if k not in ['__class__', '__filename__']})
    if os.path.split(tmp.filename)[1] != orig_filename:
        shutil.move(tmp.filename, os.path.split(tmp.filename)[0] + os.sep + os.path.split(orig_filename)[1])
        tmp.filename = os.path.split(tmp.filename)[0] + os.sep + os.path.split(orig_filename)[1]
        tmp.originalFilename = tmp.filename
        tmp.link = tmp.filename
    return tmp


# ---------------------
# backwards compatibility
# ---------------------
isNone = is_none


class OMFITfileASCII(OMFITascii):
    """
    Use of this class is deprecated: use OMFITascii instead
    """


class OMFIT_Ufile(OMFITuFile):
    """
    Use of this class is deprecated: use OMFITuFile instead
    """


class OMFITdict(SortedDict):
    """
    Use of this class is deprecated: use SortedDict instead
    """


expr_value = evalExpr


class chebyfit(omfit_classes.utils_fit.fitCH):
    """
    Use of this class is deprecated: use fitCH instead
    """


class OMFITdependenceException(RuntimeError):
    """
    Use of this class is deprecated: use RuntimeError instead
    """


# ------------------
# this version time (follows last version time in startup.py)
# ------------------
_filename = OMFITsettingsDir + os.sep + 'OMFITlastRun.txt'
if float(thisVersionTime) > float(latestVersionTime):
    with open(_filename, 'w') as _f:
        _f.write(str(thisVersionTime))

# --------------------------------------
# load main settings and override / fix
# older versions of users main settings
# NOTE: after this point on OMFIT['MainSettings'] is available and can be accessed
# --------------------------------------
def _clearDeprecatedMainSettings(MainSettings):
    # keep track if there has been a change
    updated = False

    keep = {}
    # clear if last version is before given time or if `tmpDir` is found within one month after given time
    # (this is done to manage transition between versions of OMFIT that are already running)
    if latestVersionTime < 1427916944 or (
        'SETUP' in MainSettings and 'tmpDir' in MainSettings['SETUP'] and thisVersionTime < (1427916944 + 60 * 60 * 24 * 30)
    ):
        keep['SETUP'] = {}
        keep['SETUP']['email'] = ''
        keep['SETUP']['modulesDir'] = ''
        keep['SETUP']['editor'] = ''
        keep['SETUP']['browser'] = ''
        keep['SETUP']['error_report'] = ''
        for k in ['Extensions', 'KeyBindings', 'GUIappearance']:
            if k in MainSettings['SETUP']:
                keep['SETUP'][k] = copy.deepcopy(MainSettings['SETUP'][k])
        keep['EXPERIMENT'] = {}
        keep['EXPERIMENT']['device'] = ''
        keep['EXPERIMENT']['shot'] = ''
        keep['EXPERIMENT']['time'] = ''
        keep['SERVER'] = {}
        keep['SERVER']['GA_username'] = ''
        keep['SERVER']['PPPL_username'] = ''
        keep['SERVER']['NERSC_username'] = ''
        keep['SERVER']['UCSD_username'] = ''
        keep['SERVER']['ITM_username'] = ''
        keep['SERVER']['MIT_username'] = ''
        keep['SERVER']['default'] = ''
        keep['SERVER']['idl'] = ''
        keep['SERVER']['matlab'] = ''

        tmp = prune_mask(MainSettings, keep)
        MainSettings.clear()
        MainSettings.update(tmp)
        updated = True

    if 'SERVER' in MainSettings:
        # delete deprecated servers and localhost (localhost entry will be re-created)
        for server in (
            ['thea', 'harvest', 'venus', 'venus_tmp', 'venus_scratch', 'hopper', 'zeus', 'lohan', 'philos', 'edison']
            + list(['lohan%d' % x for x in range(20)])
            + ['localhost']
        ):
            if server in list(MainSettings['SERVER'].keys()):
                del MainSettings['SERVER'][server]
                if server != 'localhost':
                    updated = '1. deprecated_server:' + server
            # delete references to the deprecated servers
            for item in list(MainSettings['SERVER'].keys()):
                if (
                    'localhost' not in [item, server]
                    and isinstance(MainSettings['SERVER'][item], str)
                    and MainSettings['SERVER'][item] == server
                ):
                    del MainSettings['SERVER'][item]
                    updated = '2. deprecated_server: (%s,%s)' % (server, item)
        # delete servers if any of their entries is set to None
        for server in list(MainSettings['SERVER'].keys()):
            if isinstance(MainSettings['SERVER'][server], namelist.NamelistName):
                for item in list(MainSettings['SERVER'][server].keys()):
                    if MainSettings['SERVER'][server][item] == None:
                        del MainSettings['SERVER'][server]
                        updated = 'none_server'
                        break
        # freeze usernames
        username_keys = [item for item in MainSettings['SERVER'] if item.endswith('_username')]
        for username_key in username_keys:
            # if OMFIT is running at a recognized institution set username to match os.environ['USER'] if OMFITexpression or empty string
            if (
                (isinstance(MainSettings['SERVER'][username_key], OMFITexpression) or not MainSettings['SERVER'][username_key])
                and ('institution' in MainSettings['SETUP'])
                and username_key == (MainSettings['SETUP']['institution'] + '_username')
            ):
                MainSettings['SERVER'][username_key] = os.environ['USER']
                updated = 'freeze_username_institution'
            # for all other servers set username to empty string if username is an OMFITexpression
            elif isinstance(MainSettings['SERVER'][username_key], OMFITexpression):
                MainSettings['SERVER'][username_key] = ''
                updated = 'freeze_username_expression'
            # NFRI renamed themselves to KFE
            if (
                'KFE_username' in MainSettings['SERVER']
                and not MainSettings['SERVER']['KFE_username']
                and 'NFRI_username' in MainSettings['SERVER']
                and MainSettings['SERVER']['NFRI_username']
            ):
                MainSettings['SERVER']['KFE_username'] = MainSettings['SERVER']['NFRI_username']

    # prevent users to change workDir in bad ways
    if 'SETUP' in MainSettings and 'workDir' in MainSettings['SETUP'] and OMFITcwd not in str(MainSettings['SETUP']['workDir']):
        MainSettings['SETUP']['workDir'] = OMFITexpression("OMFITcwd+os.sep+'runs'+os.sep")
        updated = 'workdir'

    if (
        'SETUP' in MainSettings
        and 'GUIappearance' in MainSettings['SETUP']
        and 'persistent_projectID' in MainSettings['SETUP']['GUIappearance']
    ):
        del MainSettings['SETUP']['GUIappearance']['persistent_projectID']
        updated = 'persistent_project_id'

    if 'EXPERIMENT' in MainSettings and 'runid' in MainSettings['EXPERIMENT'] and MainSettings['EXPERIMENT']['runid'] == None:
        MainSettings['EXPERIMENT']['runid'] = 'sim1'
        updated = 'experiment'

    return updated


OMFIT.reset()
_updated = _clearDeprecatedMainSettings(OMFIT['MainSettings'])
if _updated:
    OMFIT.addMainSettings(updateUserSettings=True)

# set OMFIT repos directory where the users projects are stored
# rationale: home directory have quotas, scratch directories get automatically cleaned
omfit_classes.utils_base.OMFITreposDir = (
    os.path.split(os.path.abspath(evalExpr(OMFIT['MainSettings']['SETUP']['projectsDir'])))[0] + os.sep + '.repos'
)

# ------------------------------------
# Initialize OMFIT tree
# ------------------------------------
if not np.any([('sphinx' in k and not 'sphinxcontrib' in k) for k in sys.modules]):
    OMFIT.start()
    print('Time to load omfit_tree: %g seconds' % (time.time() - _t0))

    # ------------------------------------
    # Set new modules skeleton
    # ------------------------------------
    if os.path.exists(OMFITsessionDir + os.sep + 'NEW_MODULE_skeleton'):
        shutil.rmtree(OMFITsessionDir + os.sep + 'NEW_MODULE_skeleton', ignore_errors=True)
    shutil.copytree(
        OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'skeleton' + os.sep + 'NEW_MODULE', OMFITsessionDir + os.sep + 'NEW_MODULE_skeleton'
    )
    OMFITaux['moduleSkeletonCache'] = OMFITtree(
        OMFITsessionDir + os.sep + 'NEW_MODULE_skeleton' + os.sep + 'OMFITsave.txt', quiet=True, modifyOriginal=True, readOnly=True
    )

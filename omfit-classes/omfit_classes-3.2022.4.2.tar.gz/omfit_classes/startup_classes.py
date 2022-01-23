from omfit_classes.utils_base import *

framework = False
repo = None


class OMFITobject(object):
    def __init__(self, filename, **kw):

        readOnly = kw.pop('readOnly', False)
        if readOnly:
            kw['readOnly'] = True
        file_type = kw.pop('file_type', 'file')
        if file_type == 'dir':
            kw['file_type'] = 'dir'
        kw.pop('noCopyToCWD', None)  # this is always the case when running the classes outside the framework
        self.OMFITproperties = {}
        self.OMFITproperties.update(kw)

        # NOTE: some functionalities are available only when the OMFIT framework is running
        for item in ['serverPicker', 'remote', 'server', 'tunnel', 's3bucket']:
            if item in kw:
                raise Exception('`%s` functionality is only available within the OMFIT framework' % item)

        self.modifyOriginal = True  # importing classes outside of OMFIT --always-- operates on the original files
        self.readOnly = readOnly  # readonly functionality is supported outside of framework
        self.originalFilename = filename
        self.filename = filename
        self.link = filename
        self.dynaLoad = False

        if filename is None:
            return

        # remove trailing backslash from filename
        filename = filename.rstrip(os.sep)

        # handle comma separated filenames
        if file_type == 'dir':
            fnames = filename.split(',')
            if len(fnames) > 1:
                filename = os.path.split(filename.split(',')[0])[0]

        # create file if it does not exist
        if not os.path.exists(filename) or not len(filename):
            # if a directory was NOT specified...
            if not len(os.path.split(filename)[0]) or not len(filename):
                # an empty string generates a temporary file
                if not len(filename):
                    import tempfile

                    filename = tempfile._get_default_tempdir() + os.sep + file_type + '_' + now("%Y-%m-%d__%H_%M_%S__%f")
                # create file in the current working directory
                if file_type == 'dir':
                    os.makedirs(filename)
                else:
                    open(filename, 'w').close()
            else:
                raise OMFITexception("No such file or directory: '" + filename + "'")

        # set filename attributes
        filename = os.path.abspath(filename)
        self.originalFilename = filename
        self.filename = filename
        self.link = filename

        # keep track of what classes have been loaded
        from omfit_classes.utils_base import _loaded_classes

        _loaded_classes.add(self.__class__.__name__)

    def save(self):
        """
        The save method is supposed to be overridden by classes which use OMFITobject as a superclass.
        If left as it is this method can detect if .filename was changed and if so, makes a copy from the original .filename (saved in the .link attribute) to the new .filename
        """
        return self._save_by_copy()

    def _save_by_copy(self):
        # if not exists or different
        if not (os.path.exists(self.filename) and os.path.samefile(self.link, self.filename)):

            if not os.path.exists(self.link):
                raise IOError('Missing link file ' + str(self.link))

            # remove existing file/directory if overwriting
            if not os.path.isdir(self.link):
                if os.path.exists(self.filename):
                    import filecmp

                    if filecmp.cmp(self.link, self.filename, shallow=False):
                        self.link = self.filename
                        return
                    else:
                        os.remove(self.filename)
                shutil.copy2(self.link, self.filename)
            else:
                tmp = os.getcwd()
                try:
                    # change working directory to handle possible overwriting
                    # of the current working directory or its parents
                    os.chdir('/')
                    if os.path.exists(self.filename):
                        shutil.rmtree(self.filename)
                    shutil.copytree(self.link, self.filename)
                finally:
                    os.chdir(tmp)

            self.link = self.filename

    def saveas(self, filename, remove_original_file=False, **kw):
        """
        This function changes the ``.filename`` attribute to filename and calls the ``.save()`` method and optionally remove original file.
        NOTE: use .deploy() to save an object to a given directory without changing the .filename that OMFIT uses

        :param filename: new absolute path of the filename.
                         If relative path is specified, then directory of current filename is used as root.
                         An empty filename will skip the save.

        :param remove_original_file: remove original file (forced to `False` if object is readOnly)

        :return: return value of save()
        """
        # empty filename skips the save
        if not filename:
            return

        # if not absolute path then use directory of current filename as root
        if filename.strip()[0] != os.sep:
            return self.saveas(
                os.path.split(os.path.abspath(self.filename))[0] + os.sep + filename, remove_original_file=remove_original_file, **kw
            )

        # save as
        old_filename = self.filename
        try:
            self.filename = filename
            tmp = self.save(**kw)
        except Exception:
            self.filename = old_filename
            raise

        # remove original file
        if remove_original_file and os.path.exists(old_filename) and not self.readOnly:
            if os.path.isdir(old_filename):
                shutil.rmtree(old_filename)
            else:
                os.remove(old_filename)
        return tmp

    def deploy(self, filename='', **kw):
        """
        The deploy method is used to save an OMFITobject to a location without affecting it's .filename nor .link attributes

        :param filename: filename or directory where to deploy file to
        """
        if filename == '' and self.filename:
            filename = os.path.split(self.filename)[1]

        tmpF = self.filename
        if hasattr(self, 'link'):
            tmpL = self.link

        try:
            if filename == '':
                self.filename = os.path.split(self.filename)[1]
            elif os.path.exists(filename) and os.path.isdir(filename):
                self.filename = filename + os.sep + os.path.split(tmpF)[1]
            else:
                self.filename = filename
            self.filename = os.path.abspath(self.filename)

            directory = os.path.split(self.filename)[0]
            if not os.path.exists(directory):
                os.makedirs(directory)

            self.save(**kw)

            return self.filename

        finally:
            self.filename = tmpF
            if hasattr(self, 'link'):
                self.link = tmpL

    def __deepcopy__(self, memo={}):
        """
        This method attempts to copy by pikling.
        If this fails, it will resort to calling the .duplicate() method

        :param memo: dictionary for preventing loops in deepcopy

        :return: copied object
        """
        try:
            return pickle.loads(pickle.dumps(self, pickle.HIGHEST_PROTOCOL))
        except Exception as _excp:
            printt('Failed to pickle: ' + repr(_excp) + '\nFallback on duplicating by file ' + self.filename)
            return self.duplicate(self.filename)

    def close(self):
        """
        This method:

            1. calls the .save() method, if it exists

            2. calls the .clear() method

            3. calls the .__init__() method with the arguments that were originally fed

        The purpose of this method is to unload from memory the typical OMFIT objects
        (which are a combination of SorteDict+OMFITobject classes), and has been added
        based on the considerations outlined in:
        http://deeplearning.net/software/theano/tutorial/python-memory-management.html#internal-memory-management
        http://www.evanjones.ca/memoryallocator/
        """
        if hasattr(self, 'dynaLoad') and self.dynaLoad:
            return
        if hasattr(self, 'save'):
            self.save()
        if hasattr(self, 'clear'):
            self.clear()
        self.__init__(self.filename, noCopyToCWD=True, **self.OMFITproperties)

    def __tree_repr__(self):
        if isinstance(self.filename, str):
            if os.path.isdir(self.filename):
                values = 'DIR: ' + os.path.split(self.filename)[1]
            else:
                values = 'FILE: ' + os.path.split(self.filename)[1] + '    (' + sizeof_fmt(self.filename) + ")"
        else:
            values = 'DIR/FILE: ?'
        return values, []


from omfit_classes.sortedDict import *


def test_classes_main_header():
    """
    Place this funtion after `if '__main__' == __name__:` in classes/omfit_xxx.py files
    This will:
    1. change working directory to temporary folder
    2. select matplotlib PDF backend if running without $DISPLAY variable set
    """
    # change working directory to temporary folder
    os.chdir(OMFITtmpDir)
    print('Testing class folder: ' + OMFITtmpDir)

    # select matplotlib PDF backend if running without $DISPLAY variable set
    if not os.environ.get('DISPLAY', None):
        print('Setting mpl pdf backend')
        if 'matplotlib' in sys.modules:
            from matplotlib import pyplot

            pyplot.switch_backend('pdf')
        else:
            import matplotlib

            matplotlib.use('agg')


MainScratch = scratch = {}
OMFIT = {'scratch': MainScratch}


class defaultVars(dict):
    """
    Mimic behaviour of defaultVars within OMFIT framework by allowing passing of arguments to standalone scripts at command line.
    For example:

    Given test.py:
        >> from omfit_classes.omfit_ascii import OMFITascii, defaultVars
        >> bla = defaultVars(a=1)
        >> a = bla['a']
        >> print(a)

    Allow passing of arguments with:
        python test.py a=2

    Which will print:
        2
    """

    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('scriptArgs', nargs='*')
        args = parser.parse_args()
        for item in args.scriptArgs:
            if '=' not in item:
                print(args.scriptArgs)
                raise ValueError('Must pass argument as key=value')
            tmp = item.split('=')
            key = tmp[0]
            if key not in self:
                raise ValueError('defaultVars argument `%s` not recognized. Valid arguments are: %s' % (key, self.keys()))
            value = eval('='.join(tmp[1:]))
            self[key] = value


# load the MainSettingsNamelistDump.txt file which is basically the user MainSettings
# with all of the dynamic expressions being evaluated.
from omfit_classes import namelist

OMFIT['MainSettings'] = namelist.NamelistName()
_userMainSettingsFilename = OMFITsettingsDir + os.sep + 'MainSettingsNamelistDump.txt'
_skeleton_filename = os.path.split(os.path.abspath(__file__))[0] + os.sep + 'skeleton' + os.sep + 'skeletonMainSettingsNamelist.txt'
if os.path.exists(_userMainSettingsFilename):
    for fn in [_skeleton_filename, _userMainSettingsFilename]:
        if os.path.exists(fn):
            _tmp = namelist.NamelistFile(fn)
            _tmp.load()
            recursiveUpdate(OMFIT['MainSettings'], _tmp)
else:
    # if MainSettingsNamelistDump.txt is not found then skeletonMainSettingsNamelist.txt is loaded
    # this does not have customizations about usersname and such for connections to remote servers
    # To create this file, start OMFIT frameowork and customize MainSettings via File >  Preferences GUI
    OMFIT['MainSettings'].update(namelist.NamelistFile(_skeleton_filename))
SERVER = OMFIT['MainSettings']['SERVER']

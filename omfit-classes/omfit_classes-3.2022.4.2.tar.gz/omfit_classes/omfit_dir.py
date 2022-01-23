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

from omfit_classes.omfit_path import OMFITpath
from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITdir']


class OMFITdir(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with directories

    :param filename: directory path passed to OMFITobject class

    :param extensions: dictionary mapping filename expression to OMFIT classes, for example: {'*.dat': 'OMFITnamelist', '*.xml': 'OMFITxml'}

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, extensions={}, **kw):
        SortedDict.__init__(self)
        kw['file_type'] = 'dir'
        if len(extensions):
            kw['extensions'] = extensions
            for item in extensions:
                assert isinstance(extensions[item], str), 'OMFITdir extensions can only be string'
        OMFITobject.__init__(self, filename, **kw)
        self.OMFITproperties.pop('file_type', 'dir')
        self.update_dir()

    def __call__(self):
        return self.update_dir()

    def update_dir(self):
        """
        populate current object with folders and files from self.filename directory
        """
        self.clear()
        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            tmp = dir2dict(self.filename)
            self.update(tmp[list(tmp.keys())[0]])
            for key in list(self.keys()):
                filename = self.filename + os.sep + key
                if os.path.isdir(filename):
                    self[key] = OMFITdir(filename, extensions=self.OMFITproperties.get('extensions', {}), noCopyToCWD=True)
                else:
                    match = False
                    for ext in self.OMFITproperties.get('extensions', {}):
                        import fnmatch

                        if fnmatch.fnmatch(filename, ext):
                            exec('from omfit_classes.omfit_python import ' + self.OMFITproperties['extensions'][ext])
                            self[key] = eval(self.OMFITproperties['extensions'][ext])(filename, noCopyToCWD=True)
                            match = True
                            break
                    if not match:
                        if is_binary_file(filename):
                            self[key] = OMFITpath(filename, noCopyToCWD=True)
                        else:
                            self[key] = OMFITascii(filename, noCopyToCWD=True)

    def add(self, key, obj):
        """
        Deploy OMFITojbect obj to current OMFITdir directory

        :param key: key where to add the object (NOTE: this key can have `/` separators to indicate subdirectories)

        :param obj: OMFITobject to add

        :return: OMFITobject deployed to directory
        """
        keys = key.split(os.sep)
        filename = os.sep.join([self.filename] + keys)
        obj.deploy(filename)

        # build subtree items
        loc = self
        for k, d in enumerate(keys[:-1]):
            if d not in loc:
                loc[d] = OMFITdir(os.sep.join([self.filename] + keys[: k + 1]), noCopyToCWD=True)
            loc = loc[d]

        loc[keys[-1]] = OMFITpath(filename, noCopyToCWD=True)
        return loc[keys[-1]]

    def importDir(self, subfolder=None):
        """
        This method adds the directory (possibly a specific subfolder) to the sys.path (i.e. PYTHONPATH)
        so that the python functions contained in this folder can be called from within OMFIT

        :param subfolder: subfolder under the OMFITdir object

        :return: None
        """
        if os.path.isdir(self.filename):
            if not os.path.exists(self.filename + os.sep + '__init__.py'):
                open(self.filename + os.sep + '__init__.py', 'w').close()

            tmp = self.filename
            if subfolder is not None:
                tmp = self.filename + os.sep + subfolder
            if tmp in sys.path:
                sys.path.remove(tmp)
            sys.path.insert(0, tmp)

    def __delitem__(self, key):
        filename = self.filename + os.sep + key
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)
        super().__delitem__(key)


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITdir('asd')
    tmp.add('bla/zzz/aaa.py', OMFITpath('test.py'))
    print(tmp.filename)
    assert tmp['bla']['zzz']['aaa.py'].filename.split(os.sep)[-3:] == ['bla', 'zzz', 'aaa.py']
    tmp1 = OMFITdir(tmp.filename, extensions={'*.py': 'OMFITascii'})
    print(tmp1)

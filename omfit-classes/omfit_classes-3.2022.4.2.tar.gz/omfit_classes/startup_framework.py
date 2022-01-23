import sys
import time

framework = True

print('Setting up environment...')
t_start_startup = time.time()

# ---------------------------------------
# utils_base
# ---------------------------------------
from omfit_classes.utils_base import *
from omfit_classes import utils_base
from omfit_classes.utils_base import _allOMFITobjects

try:
    repo = OMFITgit(OMFITsrc + os.sep + '..' + os.sep)
except OSError as _excp:
    raise OSError(str(_excp) + '\nPlease make sure to follow these instructions when installing OMFIT: https://omfit.io/install.html')

# ---------------------------------------
# define general directories information
# ---------------------------------------
import random

# remember starting directory
OMFITstartDir = os.getcwd()
OMFITaux['lastBrowsedDirectory'] = OMFITstartDir
OMFITaux['session_color'] = "#" + ("%06x" % random.randint(0, 16777215))

# set default starting directory for files browsing
OMFITaux['lastBrowsed']['__lastServer__'] = 'localhost'
OMFITaux['lastBrowsed']['__lastTunnel__'] = ''
OMFITaux['lastBrowsed']['localhost-'] = OMFITstartDir

# The OMFITtmpDir variable stores the temporary directory where working
# directories from multiple instances of OMFIT coexist
# The environmental variable OMFIT_TMPDIR sets the base of that directory
# It is important that OMFITtmpDir is defined in a directory that is not shared, this means that
# on clusters it should be a directory that is local to the node where OMFIT is running
OMFITtmpDir = utils_base.OMFITtmpDir
# the OMFITsessionDir variable stores the working directory for the current OMFIT session
OMFITsessionDir = utils_base.OMFITsessionDir
# the OMFITcwd variable stores the working directory for the current project
OMFITcwd = OMFITsessionDir + os.sep + 'project'
if not os.path.exists(OMFITcwd):
    os.makedirs(OMFITcwd)

# The OMFITglobaltmpDir is used to store temporary information that should be
# shared among different OMFIT sessions.
# On clusters this should be a temporary directory that is seen by all the nodes where a OMFIT could be running
_tmp = os.path.abspath(os.environ.get('OMFIT_GLOBAL_TMPDIR', os.environ.get('OMFIT_TMPDIR', os.sep + 'tmp')))
OMFITglobaltmpDir = os.sep.join([_tmp, os.environ['USER'], 'OMFIT'])
# scripts backups and auto-saves in case something goes awfully bad
# scripts backups are saved in the local temporary directory because
# their save system makes use of hard links
OMFITscriptsBackupDir = os.path.abspath(OMFITtmpDir) + '_scripts_backup'
OMFITautosaveDir = os.path.abspath(OMFITglobaltmpDir) + '_projects_autosave'

# -------------------
# OMFITobject
# -------------------
def _cleanup():
    # This function removes OMFITobject files once they get de-referenced
    # This approach was preferred over setting the OMFITobject.__del__
    # method, because the latter lead to memory leaks problems
    for filename in list(_allOMFITobjects.keys()):
        # remove broken references
        for k in reversed(range(len(_allOMFITobjects[filename]))):
            if _allOMFITobjects[filename][k]() is None:
                _allOMFITobjects[filename].pop(k)

        # remove files/directories
        if not len(_allOMFITobjects[filename]):
            del _allOMFITobjects[filename]
            if (
                int(os.environ.get('OMFIT_FILES_GC', '0'))
                and os.path.exists(filename)
                and os.path.abspath(OMFITcwd) in os.path.abspath(filename)
            ):
                try:
                    printd('REMOVING: %s' % filename, topic='gc')

                    if os.path.isdir(filename):
                        shutil.rmtree(filename, ignore_errors=True)
                    else:
                        os.remove(filename)

                    # clean empty directories
                    path = os.path.split(filename)[0]
                    while not len(glob.glob(path + os.sep + '*')):
                        printd('CLEANING: %s' % path, topic='gc')
                        shutil.rmtree(path, ignore_errors=False)
                        path = os.path.split(path)[0]

                except Exception as _excp:
                    printe(f'OMFIT temporary files cleanup error {filename}: {repr(_excp)}')


class OMFITobject(object):
    r"""
    Other OMFIT classes are a subclass of this class
    Classes which inherit from this class only have to provide a .load() and .save() which take care of
    loading and saving the content of the class from/to a file defined in the .filename attribute.
    This class takes care of creating/moving files in the OMFIT temporary working directory.
    Using .filename and .save(), this class also provides the functions .saveas() and .deploy()
    NOTE: In the end the .filename attribute will point to the OMFIT working copy of the file

    :param filename: * if modifyOriginal: use the filename as is
                     * if NOT modifyOriginal and it's an empty string generate a temporary file in the OMFITcwd directory
                     * if NOT modifyOriginal and the filename does exists copy the file to the OMFITcwd directory
                     * if NOT modifyOriginal and the filename does NOT exists and a directory was NOT specified: create a new file in the OMFITcwd directory
                     * if NOT modifyOriginal and the filename does NOT exists and a directory was specified: raise an OMFITexception

    :param file_type: `file` or `dir`
                      if `file_type=='dir'` then filename can be a string with comma-separated files that will go in the directory

    :param modifyOriginal: whether to make a copy or not of the filename provided

    :param readOnly: do not write data from the OMFIT-tree to the object (classes must use @dynaSave decorator on the `save()` method to make use of this feature)

    :param noCopyToCWD: do not make a copy of the filename (if True this setting wins over modifyOriginal).
        Differently from modifyOriginal this setting does not get propagated with the OMFITproperties.
        This parameter is mostly meant for advanced settings within the OMFIT omfit_classes.

    :param serverPicker: take server/tunnel info from MainSettings['SERVER']

    :param remote: access the filename in the remote directory

    :param server: if specified the file will be downsync from the server

    :param tunnel: access the filename via the tunnel

    :param s3bucket: name of s3 bucket to download from

    :param \**kw: dictionary intended to be used by subclassing omfit_classes. Ignored by OMFITobject.
    """
    # static variable when the objects were cleaned the last time
    cleanup_time = [0]

    def __init__(
        self,
        filename,
        file_type='file',
        modifyOriginal=False,
        readOnly=False,
        noCopyToCWD=False,
        serverPicker=None,
        remote='',
        server='localhost',
        tunnel='',
        s3bucket=None,
        **kw,
    ):

        # cleanup other OMFITobject files that are not referenced anymore
        if not len(OMFITaux['prun_process']):
            # do not call cleaning more often then once per second
            if time.time() - self.cleanup_time[0] > 1:
                _cleanup()
                self.cleanup_time[0] = time.time()

        # store extra arguments that the user passed, so that these can be used to generate the OMFITsave.txt file
        self.OMFITproperties = {}
        self.OMFITproperties.update(kw)
        self.modifyOriginal = modifyOriginal  # whether to make a copy of the file to OMFITcwd or use original file
        self.readOnly = readOnly  # whether to write data from the OMFIT-tree to the object (used by @dynaSave decorator)
        self.file_type = file_type

        self.filename = None  # current filename
        self.originalFilename = None  # used to keep memory of the original filename
        self.link = None  # used by the OMFITojbect class to copy itself

        # stop here if nothing else needs to be done
        if filename == None:
            return

        # generate a temporary directory name (safe for parallel runs)
        subprocess_dir = '_'.join(map(str, OMFITaux['prun_process']))
        if len(subprocess_dir):
            subprocess_dir = '__p' + subprocess_dir
        directory = (
            OMFITcwd
            + os.sep
            + 'objects'
            + os.sep
            + file_type
            + '_'
            + utils_base.now("%Y-%m-%d__%H_%M" + subprocess_dir + os.sep + "%S__%f")
        )
        while os.path.exists(directory):
            directory += "_"

        # if filename is empty, then generate unique filename
        if filename == '':
            filename = file_type + '_' + utils_base.now("%Y-%m-%d__%H_%M_%S__%f")
            while os.path.exists(filename):
                filename += "_"

        # download remote files
        else:
            # accept a list/tuple as "filename" with content of filename, server, and tunnel
            if isinstance(filename, (list, tuple)):
                filename, server, tunnel = filename

            # from serverPicker to server/tunnel
            elif serverPicker is not None:
                server = SERVER[serverPicker]['server']
                tunnel = SERVER[serverPicker]['tunnel']

            # remove trailing backslash from filename
            filename = str(filename).rstrip(os.sep)

            # if the filename is a remote file, download it
            if not is_localhost(server):
                from omfit_classes.OMFITx import remote_downsync

                fnames = [os.path.abspath(remote + os.sep + f) for f in filename.split(',')]
                if len(fnames) > 1 and not file_type == 'dir':
                    raise ValueError("comma separated filenames are allowed only for file-type='dir'")
                if len(fnames) > 1 and file_type == 'dir':
                    dirname = os.path.split(os.path.split(filename.split(',')[0])[0])[1]
                    remote_downsync(server=server, remote=fnames, local=directory + os.sep + dirname, tunnel=tunnel, ignoreReturnCode=True)
                    filename = os.path.abspath(directory + os.sep + dirname)
                else:
                    remote_downsync(server=server, remote=fnames, local=directory + os.sep, tunnel=tunnel, ignoreReturnCode=False)
                    filename = os.path.abspath(directory + os.sep + os.path.split(filename)[1])

                self.filename = filename
                self.originalFilename = filename
                self.link = filename
                # register file for deletion
                _allOMFITobjects.setdefault(self.filename, []).append(weakref.ref(self))
                return

            # if s3, download it
            # use `OMFITobject_fromS3` function to recover original object
            # including original class as well as keyword arguments
            if s3bucket is not None:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                s3connection = boto3.resource('s3', **boto_credentials())
                obj = s3connection.Object(s3bucket, filename)
                tmp = {k: eval(obj.metadata[k]) for k in obj.metadata if k not in ['__class__', '__filename__']}
                kw.update(tmp)
                self.OMFITproperties.update(tmp)
                filename = os.path.abspath(directory + os.sep + os.path.split(filename)[1])
                obj.download_file(filename)
                self.filename = filename
                self.originalFilename = filename
                self.link = filename
                # register file for deletion
                _allOMFITobjects.setdefault(self.filename, []).append(weakref.ref(self))
                return

        # this is the full thrue path fo the filename
        filename = os.path.expandvars(os.path.expanduser(str(filename)))

        # handle comma separated filenames
        fnames = filename.split(',')
        if len(fnames) > 1:
            if not file_type == 'dir':
                raise ValueError("comma separated filenames are allowed only for file-type='dir'")
            else:
                filename = os.path.split(filename.split(',')[0])[0]

        # if modifyOriginal or `OMFITaux['noCopyToCWD']` then just assign and exit
        # OMFITaux['noCopyToCWD'] is used in OMFIT when loading an object which is
        # already in the OMFIT current working directory
        # for example, when loading a zipped project.
        if modifyOriginal or OMFITaux['noCopyToCWD'] or noCopyToCWD:
            if not os.path.exists(filename):
                raise IOError("No such file or directory: " + repr(filename))
            filename = os.path.abspath(filename)
            self.filename = filename
            self.originalFilename = filename
            self.link = filename
            if not modifyOriginal:
                _allOMFITobjects.setdefault(self.filename, []).append(weakref.ref(self))
            return

        # Beyond this point we need to either make a copy of this file or create a new file with this name

        # if the path does not exist
        if not os.path.exists(filename):

            # if a directory was NOT specified...
            if not len(os.path.split(filename)[0]):
                # create file in OMFITcwd
                filename = os.path.abspath(directory + os.sep + filename)
                # touch the new file
                if not os.path.exists(os.path.split(filename)[0]):
                    os.makedirs(os.path.split(filename)[0])
                if file_type == 'file':
                    with open(filename, 'w') as _f:
                        pass
                elif file_type == 'dir':
                    os.makedirs(filename)
                self.originalFilename = filename
            else:
                raise OMFITexception("No such file or directory: '" + filename + "'")

        # if the path exists make a copy
        else:
            filename = os.path.abspath(filename)

            if file_type == 'dir' and not os.path.isdir(filename):
                raise OMFITexception("Expected a directory and got a file")
            if file_type == 'file' and os.path.isdir(filename):
                raise OMFITexception("Expected a file and got a directory")

            self.originalFilename = filename
            # if the file exists, and is not in the OMFITcwd, make a working copy in the OMFITcwd
            # if len(re.findall(r'^'+re.escape(OMFITcwd), filename))==0:
            if not os.path.exists(directory):
                os.makedirs(directory)
            if os.path.isdir(filename):
                if len(fnames) > 1:
                    if not os.path.exists(directory + os.sep + os.path.split(filename)[1]):
                        os.makedirs(directory + os.sep + os.path.split(filename)[1])
                    for fname in fnames:
                        if os.path.exists(fname):
                            shutil.copy2(fname, directory + os.sep + os.path.split(filename)[1] + os.sep + os.path.split(fname)[1])
                        else:
                            printw(fname + ' not found!')
                else:
                    shutil.copytree(filename, directory + os.sep + os.path.split(filename)[1])
            else:
                shutil.copy2(filename, directory + os.sep + os.path.split(filename)[1])
            filename = directory + os.sep + os.path.split(filename)[1]

        # whatever happens, make sure to store the full path
        filename = os.path.abspath(filename)
        self.filename = filename
        self.link = filename

        # make OMFIT copy user readeable, writeable (and browsable for directories)
        # Handy when interacting with GoogleDrive (see issue #4800)
        if os.path.isdir(filename):
            os.chmod(filename, os.lstat(filename).st_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            for root, dirs, files in os.walk(filename):
                for d in dirs:
                    d = os.path.join(root, d)
                    os.chmod(d, os.lstat(d).st_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                for f in files:
                    f = os.path.join(root, f)
                    os.chmod(f, os.lstat(f).st_mode | stat.S_IRUSR | stat.S_IWUSR)
        else:
            os.chmod(filename, os.lstat(filename).st_mode | stat.S_IRUSR | stat.S_IWUSR)

        # register for deletion
        _allOMFITobjects.setdefault(self.filename, []).append(weakref.ref(self))

        # keep track of what classes have been loaded
        from omfit_classes.utils_base import _loaded_classes

        _loaded_classes.add(self.__class__.__name__)

    def saveasGUI(self, filename='', pattern='*', **kw):
        r"""
        Opens GUI for .saveas() method

        :param filename: string of filename or tuple (filename,server,tunnel)

        :param serverPicker: take server/tunnel info from MainSettings['SERVER']

        :param server: server to which to upload the file

        :param tunnel: tunnel to connect to the server

        :param \**kw: keywords passed to the `save` method

        :return: tuple with (filename,server,tunnel) to which the object has been deployed, None if user aborted
        """

        kwDialog = {}
        kwDialog['serverPicker'] = 'localhost'
        kwDialog['server'] = 'localhost'
        kwDialog['tunnel'] = ''
        kwDialog['pattern'] = pattern
        kwDialog['lockServer'] = True
        kwDialog['directory'] = os.path.split(self.filename)[0]
        kwDialog['default'] = os.path.split(self.filename)[1]
        if filename:
            if isinstance(filename, str):
                filename = (filename, 'localhost', '')
            kwDialog['directory'] = os.path.split(filename[0])[0]
            kwDialog['default'] = os.path.split(filename[0])[1]

        from omfit_classes.OMFITx import SaveFileDialog

        fd = SaveFileDialog(**kwDialog)

        if fd.how:
            self.saveas(filename=fd.how[0], **kw)
            printi('Saveas ' + fd.how[0])

        return fd.how

    def saveas(self, filename, remove_original_file=False, **kw):
        """
        This function changes the ``.filename`` attribute to filename and calls the ``.save()`` method and optionally removes the original file.
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
            directory = os.path.split(self.filename)[0]
            if not os.path.exists(directory):
                os.makedirs(directory)
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

    def deploy(self, filename='', serverPicker=None, server='localhost', tunnel='', s3bucket=None, ignoreReturnCode=False, **kw):
        r"""
        The deploy method is used to save an OMFITobject to a location without affecting its .filename nor .link attributes.

        :param filename: filename or directory where to deploy file to
                         NOTE: no filename deploys file in current directory

        :param serverPicker: take server/tunnel info from MainSettings['SERVER']

        :param remote: remote working directory

        :param server: server to which to upload the file

        :param tunnel: tunnel to connect to the server

        :param s3bucket: name of s3 bucket to upload to

        :param ignoreReturnCode: ignore return code of rsync command

        :param \**kw: keywords passed to the `save` method

        :return: tuple with (filename,server,tunnel) to which the object has been deployed
        """

        filename = evalExpr(filename)  # to protect os. function from OMFITexpressions

        # from serverPicker to server/tunnel
        if serverPicker is not None:
            server = SERVER[serverPicker]['server']
            tunnel = SERVER[serverPicker]['tunnel']

        # remote deploy
        if not is_localhost(server):
            from omfit_classes.OMFITx import remote_upsync

            if filename == '':
                filename = os.path.split(self.filename)[1]
            if not len(os.path.split(os.path.abspath(filename))[0]):
                raise ValueError('Must specify full path for remote deployment')
            if os.path.split(filename)[1] != os.path.split(self.filename)[1]:
                tmpDir = OMFITtmpDir + os.sep + 'scratch_remote_deploy' + os.sep
                self.deploy(tmpDir + os.path.split(filename)[1], **kw)
                remote_upsync(
                    server=server,
                    local=tmpDir + os.path.split(filename)[1],
                    remote=os.path.split(os.path.abspath(filename))[0],
                    tunnel=tunnel,
                    ignoreReturnCode=ignoreReturnCode,
                )
            else:
                remote_upsync(
                    server=server,
                    local=self.filename,
                    remote=os.path.split(os.path.abspath(filename))[0],
                    tunnel=tunnel,
                    ignoreReturnCode=ignoreReturnCode,
                )
            return os.path.split(filename)[0] + os.path.split(filename)[1], server, tunnel

        # remote deploy to S3
        elif s3bucket is not None:
            from botocore.exceptions import ClientError

            s3connection = boto3.resource('s3', **boto_credentials())
            try:
                s3connection.meta.client.head_bucket(Bucket=s3bucket)
            except ClientError as _excp:
                # If a client error is thrown, then check that it was a 404 error.
                # If it was a 404 error, then the bucket does not exist.
                error_code = int(_excp.response['Error']['Code'])
                if error_code == 404:
                    s3connection.create_bucket(Bucket=s3bucket)
                else:
                    raise
            bucket = s3connection.Bucket(s3bucket)
            meta = copy.deepcopy(self.__save_kw__())
            meta['__class__'] = self.__class__.__name__
            meta['__filename__'] = os.path.split(self.filename)[1]
            meta = {k: repr(meta[k]) for k in list(meta.keys())}
            self.save(**kw)
            with open(self.filename, 'rb') as data:
                bucket.put_object(Key=filename, Body=data, Metadata=meta)
            return {'s3bucket': s3bucket, 'Key': filename, 'Metadata': meta}

        # local deploy
        else:
            tmpF = self.filename
            if hasattr(self, 'link'):
                tmpL = self.link

            try:
                # .deploy() dumps in local directory
                if filename == '':
                    self.filename = os.path.basename(self.filename)
                # .deploy(dir/) dumps in directory
                elif os.path.exists(filename) and os.path.isdir(filename):
                    self.filename = filename + os.sep + os.path.basename(tmpF)
                # .deploy(dir/filename) dumps in directory with filename
                else:
                    self.filename = filename
                self.filename = os.path.abspath(self.filename)

                directory = os.path.dirname(self.filename)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                self.save(**kw)

                return self.filename, server, tunnel

            finally:
                self.filename = tmpF
                if hasattr(self, 'link'):
                    self.link = tmpL

    def deployGUI(self, filename='', serverPicker=None, server='localhost', tunnel='', pattern='*', **kw):
        r"""
        Opens GUI for .deploy() method

        :param filename: string for local filename or tuple (filename,server,tunnel) for remote deployment

        :param serverPicker: take server/tunnel info from MainSettings['SERVER']

        :param remote: remote working directory

        :param server: server to which to upload the file

        :param tunnel: tunnel to connect to the server

        :param \**kw: keywords passed to the `save` method

        :return: tuple with (filename,server,tunnel) to which the object has been deployed, None if user aborted
        """

        kwDialog = {}
        kwDialog['server'] = server
        kwDialog['tunnel'] = tunnel
        kwDialog['pattern'] = pattern
        if filename:
            if isinstance(filename, str):
                kwDialog['directory'] = os.path.dirname(filename)
                kwDialog['default'] = os.path.basename(filename)
            elif isinstance(filename, (tuple, list, np.ndarray)) and len(filename) == 2:
                kwDialog['directory'] = os.path.dirname(filename[0])
                kwDialog['default'] = os.path.basename(filename[0])
                kwDialog['serverPicker'] = filename[1]
            elif isinstance(filename, (tuple, list, np.ndarray)) and len(filename) == 3:
                kwDialog['directory'] = os.path.dirname(filename[0])
                kwDialog['default'] = os.path.basename(filename[0])
                kwDialog['server'] = filename[1]
                kwDialog['tunnel'] = filename[2]
            else:
                raise ValueError('filename can be a string or a list of 3 strings for (filename,server,tunnel)')

        import omfit_classes.OMFITx

        fd = omfit_classes.OMFITx.SaveFileDialog(**kwDialog)

        if fd.how:
            self.deploy(filename=fd.how[0], server=fd.how[1], tunnel=fd.how[2], **kw)
            if is_localhost(fd.how[1]):
                printi('Deploy ' + fd.how[0])
            else:
                printi('Deploy ' + str(fd.how))

        return fd.how

    def save(self):
        """
        The save method is supposed to be overridden by classes which use OMFITobject as a superclass.
        If left as it is this method can detect if .filename was changed and if so, makes a copy from the original .filename (saved in the .link attribute) to the new .filename
        """
        return self._save_by_copy()

    def _save_by_copy(self):
        try:
            # if not exists or different
            if not os.path.exists(self.filename) or not os.path.samefile(self.link, self.filename):

                if not os.path.exists(self.link):
                    raise IOError('Missing .link file ' + str(self.link))

                # remove existing file/directory if overwriting
                # if allowed, use hard-links for files
                if not os.path.isdir(self.link):
                    if os.path.exists(self.filename):
                        if filecmp.cmp(self.link, self.filename, shallow=False):
                            self.link = self.filename
                            return
                        else:
                            os.remove(self.filename)
                    if OMFITaux['hardLinks']:
                        try:
                            os.link(self.link, self.filename)
                            printd('Hard link: %s --> %s' % (self.link, self.filename), topic='save')
                        except Exception:
                            printd('Hard link failed: %s --> %s' % (self.link, self.filename), topic='save')
                            shutil.copy2(self.link, self.filename)
                    else:
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

        finally:
            # Make sure that .link and .filename attributes are always in synch
            # We do not enforce it, and rather only check it and raise an error
            # because we want to identify if/when that does not happen.
            if not os.path.samefile(self.link, self.filename):
                raise IOError('.link and .filename attributes went out of synch!')

    def duplicate(self, filename=''):
        """
        Duplicates the OMFITobject by file copy, i.e. save this object to file, and reload it
        Note that OMFITexpressions are not going to be copied as expressions.

        :param filename: specifies a filename for the duplicated object (same rules for OMFITobject __init__ function apply)

        :return: duplicated object
        """

        # save original filename and link
        tmpF = self.filename, self.link

        try:
            # generate an empty file in the OMFIT temporary directory with the desired filename
            if not len(filename):
                filename = os.path.split(self.filename)[1]
            tmp = OMFITobject(filename, file_type=['file', 'dir'][os.path.isdir(self.filename)])

            # change the object .filename and save it
            self.filename = tmp.filename
            self.save()

            # reload object passing the OMFITproperties of the current object
            tmp = self.__class__(self.filename, **self.OMFITproperties)

        finally:
            # no matter what happens restore original filename and link
            self.filename, self.link = tmpF

        return tmp

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

    def read(self, filename=None):
        """
        Read the file specified in self.filename.
        If this file is a .zip file, deflate it and read it.
        If multiple files are present in the zip, specify what file is to be extracted with the `filename` keyword or a dictionary with all the extracted files will read and be returned.

        :param filename: specific file to be read

        :return: string with content of file or dictionary if zip file with multiple files in it
        """
        if zipfile.is_zipfile(self.filename):
            input_zip = zipfile.ZipFile(self.filename, allowZip64=True)
            if len(input_zip.namelist()) == 1:
                return input_zip.read(input_zip.namelist()[0])
            elif filename is not None:
                return input_zip.read(filename)
            else:
                return {filename: input_zip.read(filename) for filename in input_zip.namelist()}
        else:
            with open(self.filename, 'r') as f:
                return f.read()

    def plotFigure(self, *args, **kw):
        r"""
        If the subclass has a .plot() method this will be called as .plot(\**kw) after pyplot.figure(\*args) is called

        :param \*args: arguments to be passed to pyplot.figure()

        :param \**kw: keywords argument to be passed to .plot()

        :return: returns whatever the .plot() method returns
        """
        if hasattr(self, 'plot'):
            pyplot.figure(*args)
            try:
                return self.plot(**kw)
            finally:
                # if nothing has been plotted close the figure which was just opened
                if len(pyplot.gcf().get_children()) < 2:
                    pyplot.close(pyplot.gcf())

    def __str__(self):
        """
        String representation is simply the .filename attribute

        :return: .filename attribute
        """
        return self.filename

    def _repr(self):
        """
        :return: string representation of self.OMFITproperties dictionary
        """
        line = []
        for k, v in list(self.OMFITproperties.items()):
            line.append('%s=%s' % (k, repr(v)))
        return ', '.join(line)

    def __repr__(self):
        """
        Representation is simply the .filename attribute

        :return: .filename attribute
        """
        return self.filename

    def __tree_repr__(self):
        if isinstance(self.filename, str):
            if os.path.isdir(self.filename):
                values = 'DIR: ' + os.path.split(self.filename)[1]
            else:
                values = 'FILE: ' + os.path.split(self.filename)[1] + '    (' + sizeof_fmt(self.filename) + ")"
        else:
            values = 'DIR/FILE: ?'
        return values, []

    def __save_kw__(self):
        """
        :return: generate the kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        return self.OMFITproperties

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

    @property
    def readOnly(self):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        return self.OMFITproperties.get('readOnly', False)

    @readOnly.setter
    def readOnly(self, value):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        if value:
            self.OMFITproperties['readOnly'] = value
        elif 'readOnly' in self.OMFITproperties:
            del self.OMFITproperties['readOnly']

    @property
    def modifyOriginal(self):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        return self.OMFITproperties.get('modifyOriginal', False)

    @modifyOriginal.setter
    def modifyOriginal(self, value):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        if value:
            self.OMFITproperties['modifyOriginal'] = value
        elif 'modifyOriginal' in self.OMFITproperties:
            del self.OMFITproperties['modifyOriginal']

    @property
    def file_type(self):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        return self.OMFITproperties.get('file_type', 'file')

    @modifyOriginal.setter
    def file_type(self, value):
        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}
        if value not in ['file', 'dir']:
            raise ValueError('file_type option can only be `file` or `dir`')
        if value == 'dir':
            self.OMFITproperties['file_type'] = value
        elif 'file_type' in self.OMFITproperties:
            del self.OMFITproperties['file_type']


def OMFITpickle(filename, kind='filename', limit=None, squeeze=True, **kw):
    r"""
    This function conveniently un-pickles Python pickled data saved in filename/string/buffer/file_descriptor
    NOTE: chains of pickles will all be un-pickled into a list of objects

    :param filename: filename/string/buffer/file_descriptor to unpickle

    :param kind: one of 'filename', 'string', 'buffer', 'file_descriptor'

    :param limit: maximum number of objects to unpickle from pickle chain

    :param squeeze: if False, a list of objects is always returned, even when there is only one object in the pickle chain

    :param \**kw: if kind=='filename' extra keywords arguments are passed to OMFITobject (e.g. download remote object by using `serverPicker` argument)

    :return: list of unpickled objects
    """

    def readAll(f, objs):
        k = 0
        while True:
            try:
                objs.append(pickle.load(f))
                k += 1
            except EOFError:
                break
            if limit and k + 1 > limit:
                break

    objs = []
    if kind == 'filename':
        if len(kw):
            kw['modifyOriginal'] = True
            filename = OMFITobject(filename, **kw).filename
        filename = os.path.expandvars(os.path.expanduser(filename))
        with open(filename, 'rb') as f:
            readAll(f, objs)
    elif kind == 'string':
        from io import BytesIO

        readAll(BytesIO(filename), objs)
    elif kind == ['buffer', 'file_descriptor']:
        readAll(filename, objs)
    if squeeze and len(objs) == 1:
        return objs[0]
    else:
        return objs


# --------------------
# external packages imports
# --------------------
from externalImports import *

# --------------------
# set OMFIT-tree root
# --------------------
from omfit_classes.sortedDict import *

OMFIT = SortedDict()

# --------------------
# namelist
# --------------------
from omfit_classes.namelist import *
import omfit_classes.namelist
import omfit_classes.namelist as namelist

# --------------------
# import utilities
# --------------------
from utils import *
from utils import _available_to_user_math, _available_to_user_util, _available_to_user_plot
from omfit_classes.utils_fusion import _available_to_user_fusion, is_device, tokamak
import utils

# --------------------
# import omfit plot
# --------------------
from omfit_plot import *

# ----------------------------------
# find what OMFIT version is running
# ----------------------------------
repo_active_branch, repo_active_branch_commit, repo_str = repo.active_branch()
thisVersionTime = repo.get_commit_date('HEAD')

# ------------------
# last version time
# ------------------
_filename = OMFITsettingsDir + os.sep + 'OMFITlastRun.txt'
if os.path.exists(_filename):
    try:
        with open(_filename, 'r') as _f:
            latestVersionTime = float(_f.read())
    except Exception:
        latestVersionTime = os.path.getmtime(_filename)
else:
    latestVersionTime = time.time()

# -------------
# SERVER class
# -------------
def _strip_workernode_from_server(server):
    worker_name = re.sub(r'([^\d\W])([\-0-9]*)', r'\1', server)
    worker_node = re.sub(r'([^\d\W])([\-0-9]*)', r'\2', server)
    return worker_name, worker_node


def user_server_port(server):
    """
    parses strings in the form of username@server.somewhere.com:22

    :param server: input string

    :return: tuple of three strings with user,server,port
    """
    server = evalExpr(server)
    if ':' not in server:
        server = server + ':'
    if '@' not in server:
        server = '@' + server
    match = r'([\w\-\.]*@)([\w\-\.]*)(:[0-9]*)'
    user = re.sub(match, r'\1', server).strip('@')
    port = re.sub(match, r'\3', server).strip(':')
    server = re.sub(match, r'\2', server)
    return user, server, port


class _SERVER(dict):
    """
    Class used to handle servers definitions under OMFIT['MainSettings']['SERVER']
    """

    def __setattr__(self, attr, value):
        if SERVER is None or self is not SERVER:
            dict.__setattr__(self, attr, value)

    def __str__(self):
        return str(OMFIT['MainSettings']['SERVER'])

    def __repr__(self):
        return repr(OMFIT['MainSettings']['SERVER'])

    def handleServer(self, server):
        # server0: is what the user passed
        # server : is the interpreted server
        server0 = server = evalExpr(server)

        # all done if server is one of the NamelistName
        if server in [
            k for k in list(OMFIT['MainSettings']['SERVER'].keys()) if isinstance(OMFIT['MainSettings']['SERVER'][k], namelist.NamelistName)
        ]:
            return server0, server

        # if server is a module, then get the module serverPicker
        if isinstance_str(server, 'OMFITmodule'):
            if 'serverPicker' in server['SETTINGS']['REMOTE_SETUP']:
                server = str(server['SETTINGS']['REMOTE_SETUP']['serverPicker'])

        # if there is a string in the SERVERS, then follow the links (strings)
        while server in list(OMFIT['MainSettings']['SERVER'].keys()) and isinstance(evalExpr(OMFIT['MainSettings']['SERVER'][server]), str):
            server = evalExpr(OMFIT['MainSettings']['SERVER'][server])

        # recognize full server string
        server_name = parse_server(server)[2]  # only the server name
        if ('.' in server_name or ':' in server) and server not in list(OMFIT['MainSettings']['SERVER'].keys()):
            for server1 in list(OMFIT['MainSettings']['SERVER'].keys()):
                tmp = evalExpr(OMFIT['MainSettings']['SERVER'][server1])
                if not isinstance(tmp, namelist.NamelistName) or 'server' not in tmp:
                    continue
                known_server = parse_server(tmp['server'])[2]

                if (
                    server_name == known_server
                    or _strip_workernode_from_server(server_name)[0] == _strip_workernode_from_server(known_server)[0]
                ):  # match workernode
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", server_name):
                        server = server1
                    elif _strip_workernode_from_server(server_name)[0] == _strip_workernode_from_server(known_server)[0]:
                        server = parse_server(server0)[2].split('.')[0]
                    else:
                        server = server1
                    break

        return server0, server

    def _handleServer(f):
        """
        Decorator which calls `handleServer` method
        """

        @functools.wraps(f)
        def handleServer(self, server):
            server0, server = self.handleServer(server)
            return f(self, server, server0)

        return handleServer

    @_handleServer
    def __getitem__(self, server, server0):
        # handle entries in SERVERS
        if server in OMFIT['MainSettings']['SERVER'] and isinstance(OMFIT['MainSettings']['SERVER'][server], namelist.NamelistName):
            return OMFIT['MainSettings']['SERVER'][server]

        # look for the server0 verbatim
        for srv in OMFIT['MainSettings']['SERVER']:
            if isinstance(OMFIT['MainSettings']['SERVER'][srv], namelist.NamelistName):
                if (
                    'server' in OMFIT['MainSettings']['SERVER'][srv]
                    and user_server_port(OMFIT['MainSettings']['SERVER'][srv]['server'])[1] == user_server_port(server0)[1]
                ):
                    return OMFIT['MainSettings']['SERVER'][srv]

        # if not found, then see if it can be split in worker name and node number
        worker, node = _strip_workernode_from_server(server)
        if worker != server and (
            worker in list(OMFIT['MainSettings']['SERVER'].keys())
            and isinstance(OMFIT['MainSettings']['SERVER'][worker], namelist.NamelistName)
        ):
            tmp = namelist.NamelistName()
            tmp.update({item: evalExpr(OMFIT['MainSettings']['SERVER'][worker][item]) for item in OMFIT['MainSettings']['SERVER'][worker]})
            parsed_server = list(parse_server(tmp['server']))
            nds = parsed_server[2].split('.')
            if node:
                nds[0] = _strip_workernode_from_server(nds[0])[0] + node
            parsed_server[2] = '.'.join(nds)
            tmp['server'] = assemble_server(*parsed_server)
            return tmp

        # prepare server string for output to terminal
        if not isinstance(server, str):
            server = ''
        else:
            server = ' `' + server + '`'

        # raise an error
        raise KeyError('Server ' + server + " was not found in OMFIT['MainSettings']['SERVER']")

    def __call__(self, server):
        """
        The call function is used to resolve a server name

        :param server: server to be resolved

        :return: resolved server name
        """
        return self.handleServer(server)[1]

    def listServers(self):
        """
        function that returns dictionary with server names and their server info

        NOTE: servers that have blank username are not shown

        :return: dictionary
        """
        output = {}
        for k in sorted(OMFIT['MainSettings']['SERVER'].keys()):
            if isinstance(OMFIT['MainSettings']['SERVER'][k], namelist.NamelistName) and 'server' in OMFIT['MainSettings']['SERVER'][k]:
                try:
                    if parse_server(OMFIT['MainSettings']['SERVER'][k]['server'], default_username='')[0]:
                        kd = k + ' -- ' + OMFIT['MainSettings']['SERVER'][k]['server']
                        output[k] = kd
                except Exception:
                    pass
        # always add the loscalhost to the list (even if it could be a string pointing to another server)
        output['localhost'] = 'localhost -- localhost'
        return output

    def __iter__(self):
        for k in list(self.keys()):
            yield k

    def keys(self):
        return list(self.listServers().keys())

    def setLocalhost(self):
        # set localhost to the known servers
        for k in list(SERVER.keys()):
            if k != 'localhost' and is_localhost(k):
                del OMFIT['MainSettings']['SERVER']['localhost']
                OMFIT['MainSettings']['SERVER']['localhost'] = k
                break


SERVER = None
SERVER = _SERVER()

# extend the is_server and is_localhost functions to interface with the MainSettings['SERVER']
# this allows checking definitions such as `default`, `idl`, `matlab`, ...
_is_server = utils_base.is_server


def is_server(serverA, serverB):
    """
    Checks if `serverA` and `serverB` are the same server

    :param serverA: server string

    :param serverB: server string (or list of strings)

    :return: serverB that matches serverA, otherwise False
    """
    serverA = evalExpr(serverA)
    serverB_ = tolist(evalExpr(serverB))
    for serverB in serverB_:
        tmp = _is_server(serverA, serverB)
        if not tmp and serverA in OMFIT['MainSettings']['SERVER'] and serverB in OMFIT['MainSettings']['SERVER']:
            tmp = _is_server(SERVER(serverA), SERVER(serverB))
        if not tmp and is_localhost(serverA) and is_localhost(serverB):
            tmp = True
        if tmp:
            return serverB
    return False


utils_base.is_server = is_server

_is_localhost = utils_base.is_localhost


def is_localhost(server, looseCheck=True):
    """
    Checks if `server` is the localhost.
    If `server` is None or an empty string then returns True.
    `server` can be a string in the format username@server:port

    :param server: server string (or list of strings)

    :param looseCheck: loosely check if `server` string is contained in the localhost names

    :return: server that is localhost, otherwise False
    """
    server_ = tolist(evalExpr(server))
    for server in server_:
        if (
            'MainSettings' in OMFIT
            and 'SERVER' in OMFIT['MainSettings']
            and 'localhost' in OMFIT['MainSettings']['SERVER']
            and isinstance(OMFIT['MainSettings']['SERVER']['localhost'], str)
            and OMFIT['MainSettings']['SERVER']['localhost'] == server
        ):
            return server
        tmp = _is_localhost(server, looseCheck=looseCheck)
        if tmp:
            return 'localhost'
        if not tmp and 'MainSettings' in OMFIT and server in OMFIT['MainSettings']['SERVER']:
            tmp = _is_localhost(SERVER(server), looseCheck=looseCheck)
            if tmp:
                return server
        if not tmp and 'MainSettings' in OMFIT and 'localhost' in OMFIT['MainSettings']['SETUP']:
            server = parse_server(server)[2]
            tmp = np.any([re.match(localhost, server) for localhost in tolist(OMFIT['MainSettings']['SETUP']['localhost'])])
            if tmp:
                return server
    return False


utils_base.is_localhost = is_localhost

# overwite functions from omfit_classes.utils_base and add some from omfit_classes.utils_fusion
for _k in [is_localhost, is_server, is_institution, is_device, tokamak]:
    _available_to_user_util(_k)

# -------------------
# users credentials
# -------------------
def boto_credentials():
    credentials = {}
    credentials['region_name'] = 'us-east-1'
    credentials['aws_access_key_id'] = 'AKIAJTACQKI5H5HNQCWA'
    credentials['aws_secret_access_key'] = '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'
    try:
        if evalExpr(SERVER['gadb-harvest']['aws_credentials_file']):
            with open(evalExpr(SERVER['gadb-harvest']['aws_credentials_file']), 'r') as f:
                lines = f.readlines()
            for line in lines:
                if '=' in line:
                    credentials[line.split('=')[0].strip()] = line.split('=')[1].strip()
    except Exception as _excp:
        printe(repr(_excp))
    return credentials


# -------------------
# diagnostic outputs
# -------------------
print('-' * 20)
print(' '.join(platform.uname()))
print(repo_str)
print('Python executable'.ljust(22) + ': ' + sys.executable)
print('Installation type'.ljust(22) + ': ' + ['PERSONAL', 'PUBLIC'][os.path.exists(os.sep.join([OMFITsrc, '..', 'public']))])
_OMFIT_important_directories = [
    'OMFITstartDir',
    'OMFITsrc',
    'OMFITsettingsDir',
    'OMFITsessionsDir',
    'OMFITcontrolmastersDir',
    'OMFITscriptsBackupDir',
    'OMFITautosaveDir',
    'OMFITtmpDir',
    'OMFITsessionDir',
    'OMFITcwd',
]
for _k in _OMFIT_important_directories:
    print(_k.ljust(22) + ': ' + eval(_k))
print('-' * 20)

sys.__stdout__.write('Time to load startup_framework: %g seconds\n' % (time.time() - t_start_startup))
sys.__stdout__.flush()

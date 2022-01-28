import contextlib
import errno
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import os
import os.path
import shutil
import tempfile
import glob
import platform


class LocalFSClient:

    def removeFolder(self, path, remove_self=True):
        shutil.rmtree(path, ignore_errors=True)
        if not remove_self:
            self.createFolder(path)

    def removeFile(self, path, wild=False):
        try:
            if wild:
                for fl in glob.glob(path):
                    os.remove(fl)
            else:
                os.remove(path)
        except OSError:
            pass

    def isFileExists(self, path):
        return os.path.isfile(path)

    def isDirExists(self, path):
        return os.path.exists(path)

    # def saveSingleSCV(self, full_path, new_path):
    #     listFiles = os.listdir(full_path)

    #     for item in listFiles:
    #         if item.endswith(".csv"):
    #             os.rename(os.path.join(full_path, item), new_path)
    #             break

    #     self.removeFolder(full_path)

    def createFolder(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass
            #logging.exception("createFolder failed")
        self.listFolder(self.getParentFolder(path))

    def createParentFolder(self, path):
        parent = os.path.dirname(path)
        self.createFolder(parent)

    def getParentFolder(self, path):
        return os.path.dirname(path)

    def readTextFile(self, path):
        import codecs

        self.listFolder(self.getParentFolder(path))
        with codecs.open(path, "r", encoding='utf-8') as file:
            return file.read()

    def writeTextFile(self, path, data, atomic=False):
        self.createParentFolder(path)

        if atomic:
            with self.open_atomic(path, "w") as file:
                file.write(data)
        else:
            from .FSClient import FSClient
            self.removeFile(path)

            with FSClient().open(path, "w") as file:
                try:
                    file.write(data)
                finally:
                    file.flush()  # flush file buffers
                    os.fsync(file.fileno())

        self.readTextFile(path)

    # def open(self, path, mode, num_tries=20):
    #     import time
    #     import codecs
    #     import gzip

    #     nTry = 0
    #     while nTry <= num_tries:
    #         try:
    #             if path.endswith('.gz'):
    #                 return codecs.getreader('utf-8')(gzip.open(path, mode), errors='replace')

    #             return codecs.open(path, mode, encoding='utf-8', errors='replace')
    #         except Exception as e:
    #             if nTry >= num_tries:
    #                 raise

    #         if mode == 'w':
    #             self.removeFile(path)

    #         nTry = nTry + 1
    #         time.sleep(1)

    def listFolder(self, path, wild=False, removeFolderName=True, meta_info=False):
        res = []
        try:
            if wild:
                glob_res = glob.glob(path)
                if removeFolderName:
                    len_parent = len(os.path.dirname(path))+1
                    for file in glob_res:
                        res.append(file[len_parent:])
                else:
                    res = glob_res
            else:
                dir_res = os.listdir(path)
                if not removeFolderName:
                    for file in dir_res:
                        res.append(os.path.join(path, file))
                else:
                    res = dir_res

        except OSError:
            pass

        if meta_info:
            result_meta = []

            parent_folder = ""
            if removeFolderName:
                if wild:
                    parent_folder = os.path.dirname(path)
                else:
                    parent_folder = path

            for file_path in res:
                result_meta.append({'path': file_path,
                    'last_modified': self.getMTime(os.path.join(parent_folder, file_path)),
                    'size': self.getFileSize(os.path.join(parent_folder, file_path))})

            res = result_meta

        return res

    def getMTime(self, path):
        return os.path.getmtime(path)

    def getFileSize(self, path):
        return os.path.getsize(path)

    @contextlib.contextmanager
    def open_atomic(self, path, mode):
        parent = self.getParentFolder(os.path.abspath(path))
        self.listFolder(parent)

        temp_dir = self.get_temp_folder()
        try:
            temp_path = os.path.join(temp_dir, os.path.basename(path))
            # logging.info('LocalFSClient.open_atomic: open {}'.format(repr(temp_path)))
            with open(temp_path, mode) as f:
                try:
                    yield f
                finally:
                    f.flush()  # flush file buffers
                    os.fsync(f.fileno())  # ensure all data are written to disk
            # logging.info('LocalFSClient.open_atomic: written {}'.format(repr(temp_path)))
            if platform.system() == "Windows":
                if os.path.exists(path):
                    os.remove(path)

            try:
                os.rename(temp_path, path)  # atomic move to target place
                # logging.info('LocalFSClient.open_atomic: renamed {} to {}'.format(repr(temp_path), repr(path)))
            except os.error as e:
                # Fix OSError: [Errno 18] Invalid cross-device link
                if e.errno == errno.EXDEV:
                    shutil.copy(temp_path, path)
                    os.remove(temp_path)
                else:
                    raise e
        finally:
            self.removeFolder(temp_dir)
            # logging.info('LocalFSClient.open_atomic: removed {}'.format(repr(temp_dir)))

    def get_temp_folder(self):
        if os.environ.get('AUGER_LOCAL_TMP_DIR'):
            self.createFolder(os.environ.get('AUGER_LOCAL_TMP_DIR'))

        return tempfile.mkdtemp(dir=os.environ.get('AUGER_LOCAL_TMP_DIR'))

    @contextlib.contextmanager
    def save_atomic(self, path):
        temp_dir = self.get_temp_folder()
        try:
            temp_path = os.path.join(temp_dir, os.path.basename(path))
            yield temp_path
        finally:
            self.removeFolder(temp_dir)

    def moveFile(self, path_src, path_dst):
        if platform.system() == "Windows":
            if os.path.exists(path_dst):
                os.remove(path_dst)

        #logging.info("moveFile from %s to %s"%(path_src, path_dst))
        os.rename(path_src, path_dst)  # atomic move to target place

    def copyFile(self, path_src, path_dst):
        if self.isFileExists(path_dst):
            self.removeFile(path_dst)

        shutil.copy(path_src, path_dst)

    def copyFiles(self, path_src, path_dst):
        if self.isFileExists(path_dst):
            self.removeFile(path_dst)

        self.createFolder(path_dst)

        for fl in glob.glob(path_src):
            shutil.copy(fl, path_dst)

    def copyFolder(self, path_src, path_dst):
        shutil.copytree(path_src, path_dst)

    def archiveDir(self, path_src, format):
        shutil.make_archive(path_src, format, path_src)

    def downloadFile(self, path, local_path):
        from urllib.request import urlretrieve
        from auger_ml.Utils import url_encode

        self.createParentFolder(local_path)
        if local_path and local_path.startswith("/var/src"):
            #For tests
            urlretrieve(url_encode(path), local_path)
        else:
            local_filename, headers = urlretrieve(url_encode(path))
            self.moveFile( local_filename, local_path )
        # with FSClient().open(local_file_path, 'wb') as output:
        #     while True:
        #         data = req.read(1024*1024)
        #         if data:
        #             output.write(data)
        #         else:
        #             break


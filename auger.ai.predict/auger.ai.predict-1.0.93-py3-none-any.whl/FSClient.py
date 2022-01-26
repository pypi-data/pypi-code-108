from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import os
import contextlib
import time
from urllib.parse import urlparse

from .LocalFSClient import LocalFSClient


class FSClient:

    @staticmethod
    def isS3Path(path):
        return path.startswith("s3")

    @staticmethod
    def _getFSClientByPath(path):
        if path.startswith("s3"):
            from .S3FSClient import S3FSClient
            return S3FSClient()
        else:
            return LocalFSClient()

    def createFolder(self, path):
        client = self._getFSClientByPath(path)
        client.createFolder(path)

    def createParentFolder(self, path):
        client = self._getFSClientByPath(path)
        client.createFolder(self.getParentFolder(path))

    def getParentFolder(self, path):
        return os.path.dirname(path)

    def removeFolder(self, path, remove_self=True):
        client = self._getFSClientByPath(path)
        client.removeFolder(path, remove_self)

    def removeFile(self, path, wild=False):
        client = self._getFSClientByPath(path)
        client.removeFile(path, wild)

    # def saveSingleSCV(self, path, new_path):
    #     client = self._getFSClientByPath(path)
    #     client.saveSingleSCV(path, new_path)

    # def open(self, path, mode):
    #     client = self._getFSClientByPath(path)
    #     return client.open(path, mode)

    def get_smart_open_transport_params(self, path):
        if self.isS3Path(path):
            client = self._getFSClientByPath(path)
            return client.get_smart_open_transport_params()

        return None

    def open(self, path, mode, num_tries=20, encoding='utf-8'):
        import warnings

        if self.isS3Path(path) and 'r' in mode:
            client = self._getFSClientByPath(path)
            client.wait_for_path(path)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            import smart_open

            nTry = 0
            while nTry <= num_tries:
                try:
                    #TODO: support append mode for s3
                    return smart_open.open(path, mode,
                        encoding=encoding, transport_params=self.get_smart_open_transport_params(path))
                except Exception as e:
                    if nTry >= num_tries:
                        raise

                if 'w' in mode:
                    self.removeFile(path)

                nTry = nTry + 1
                time.sleep(1)

    @contextlib.contextmanager
    def s3fs_open(self, path, mode= 'rb'):
        if self.isS3Path(path):
            client = self._getFSClientByPath(path)
            path = client.s3fs_open(path, mode)

        yield path

    def listFolder(self, path, wild=False, removeFolderName=True, meta_info=False):
        client = self._getFSClientByPath(path)

        if wild:
            if not client.isDirExists(self.getParentFolder(path)):
                return []
        else:
            if not client.isDirExists(path):
                return []

        return client.listFolder(path, wild=wild, removeFolderName=removeFolderName, meta_info=meta_info)

    def getMTime(self, path):
        client = self._getFSClientByPath(path)
        return client.getMTime(path)

    def getFileSize(self, path):
        client = self._getFSClientByPath(path)
        return client.getFileSize(path)

    # @classmethod
    # def openFile(cls, path, mode):
    #     client = cls._getFSClientByPath(path)
    #     return client.open(path, mode)

    def isFileExists(self, path):
        client = self._getFSClientByPath(path)
        return client.isFileExists(path)

    def isDirExists(self, path):
        client = self._getFSClientByPath(path)
        return client.isDirExists(path)

    def readTextFile(self, path):
        client = self._getFSClientByPath(path)
        return client.readTextFile(path)

    def writeTextFile(self, path, data, atomic=False):
        client = self._getFSClientByPath(path)
        client.writeTextFile(path, data, atomic=atomic)

    def writeJSONFile(self, path, data, atomic=False, allow_nan=False):
        from .Utils import json_dumps_np
        self.writeTextFile(path, json_dumps_np(
            data, allow_nan=allow_nan), atomic=atomic)

    def updateJSONFile(self, path, data, atomic=False, allow_nan=False):
        from .Utils import json_dumps_np
        fileData = self.readJSONFile(path)
        fileData.update(data)
        self.writeTextFile(path, json_dumps_np(
            fileData, allow_nan=allow_nan), atomic=atomic)

    def readJSONFile(self, path, check_if_exist=True, wait_for_file=False):
        from auger_ml.Utils import convertStringsToUTF8
        import json

        if not self.isS3Path(path):
            self.listFolder(self.getParentFolder(path))

        self.waitForFile(path, wait_for_file=wait_for_file)

        if check_if_exist and not self.isFileExists(path):
            return {}

        nTry = 0
        while nTry < 10:
            json_text = self.readTextFile(path)
            try:
                return json.loads(json_text, object_hook=convertStringsToUTF8)
            except Exception as e:
                logging.error("Load json failed: %s.Text: %s" % (repr(e), json_text))
                nTry += 1
                time.sleep(2)

        return {}

    def waitForFile(self, path, wait_for_file, num_tries=30, interval_sec=1):
        if wait_for_file:
            nTry = 0
            while nTry <= num_tries:
                if self.isFileExists(path):
                    break

                if self.isFileExists(path):
                    break

                logging.info("File %s does not exist. Wait for %s sec" %
                             (path, interval_sec))

                nTry = nTry + 1
                time.sleep(interval_sec)

            return self.isFileExists(path)

        return True

    def loadJSONFiles(self, paths):
        result = []
        for path in paths:
            try:
                result.append(self.readJSONFile(path))
            except Exception as e:
                logging.exception("loadJSONFiles failed.")

        return result

    def copyFile(self, path_src, path_dst, check_if_exist=True):

        if check_if_exist:
            client = self._getFSClientByPath(path_src)
            if not client.isFileExists(path_src):
                return

        client = self._getFSClientByPath(path_dst)
        client.copyFile(path_src, path_dst)

    def copyFiles(self, path_src, path_dst):
        client = self._getFSClientByPath(path_src)
        client.copyFiles(path_src, path_dst)

    def archiveDir(self, path_src, fmt='zip'):
        if self.isS3Path(path_src):
            localClient = LocalFSClient()

            with localClient.save_atomic(path_src) as local_path:
                logging.info("archiveDir local path:%s"%local_path)

                clientS3 = self._getFSClientByPath(path_src)
                clientS3.downloadFolder(path_src, local_path)

                localClient.archiveDir(local_path, fmt)

                clientS3.moveFile(local_path+'.zip', path_src+'.zip')
                return

        client = self._getFSClientByPath(path_src)
        client.archiveDir(path_src, fmt)

    def copyFolder(self, path_src, path_dst):
        if self.isDirExists(path_dst):
            self.removeFolder(path_dst)

        if self.isS3Path(path_dst):
            client = self._getFSClientByPath(path_dst)
            client.copyFolder(path_src, path_dst)
        else:
            client = self._getFSClientByPath(path_src)
            client.copyFolder(path_src, path_dst)

    @staticmethod
    def _save_to_pickle(obj, path, compress):
        import joblib

        joblib.dump(obj, path, compress=compress, protocol=4)

    @staticmethod
    def _save_to_feather(obj, path, compress):
        from pyarrow import feather

        if compress == 0:
            compress = None

        feather.write_feather(obj, path, compression=compress)

    def saveObjectToFile(self, obj, path, fmt="pickle"):

        self.removeFile(path)
        self.createParentFolder(path)

        try:
            compress = 0
            if path.endswith('.gz'):
                compress = ('gzip', 3)
            elif path.endswith('.zstd'):
                compress = "zstd"
            elif path.endswith('.lz4'):
                compress = "lz4"

            if self.isS3Path(path):
                with self.save_atomic(path) as local_path:
                    if fmt == "pickle":
                        FSClient()._save_to_pickle(obj, local_path, compress=compress)
                    elif fmt == "feather":
                        FSClient()._save_to_feather(obj, local_path, compress=compress)
            else:
                if fmt == "pickle":
                    FSClient()._save_to_pickle(obj, path, compress=compress)
                elif fmt == "feather":
                    FSClient()._save_to_feather(obj, path, compress=compress)

        except:
            self.removeFile(path)
            raise

    @contextlib.contextmanager
    def save_atomic(self, path, move_file=True):
        localClient = LocalFSClient()

        with localClient.save_atomic(path) as local_path:
            yield local_path

            if move_file:
                client = self._getFSClientByPath(path)
                client.moveFile(local_path, path)

    @contextlib.contextmanager
    def save_local(self, path, move_file=True):
        if self.isS3Path(path):
            localClient = LocalFSClient()

            with localClient.save_atomic(path) as local_path:
                yield local_path

                if move_file:
                    client = self._getFSClientByPath(path)
                    client.moveFile(local_path, path)
        else:
            yield path

    def moveFile(self, path_src, path_dst):
        #print(path_src, path_dst)

        client = self._getFSClientByPath(path_dst)
        client.moveFile(path_src, path_dst)

    def downloadFile(self, path, local_path):
        if path.startswith("http:") or path.startswith("https:"):
            client = self._getFSClientByPath(local_path)
            client.downloadFile(path, local_path)
        elif self.isS3Path(path):
            client = self._getFSClientByPath(path)
            client.downloadFile(path, local_path)
        else:
            self.copyFile(path, local_path)

    def get_s3_bucket_from_path(self, data_path):
        url = urlparse(data_path)

        if url.scheme.lower() == 's3':
            return url.netloc

    def loadObjectFromFile(self, path, use_local_cache=False):
        import joblib

        path_to_load = None
        if self.isS3Path(path):
            if use_local_cache:
                bucket = self.get_s3_bucket_from_path(path)

                if bucket:
                    local_path = path.replace("s3://" + bucket, os.environ.get("AUGER_LOCAL_TMP_DIR", ''))
                else:
                    local_path = path

                #logging.info("Local cache path: %s"%local_path)
                if not self.isFileExists(local_path):
                    local_lock_path = local_path + '.lock'
                    self.createParentFolder(local_lock_path)
                    f_lock = None
                    try:
                        f_lock = open(local_lock_path, 'x')
                    except Exception as e:
                        #logging.exception("Open lock file failed.")
                        pass

                    if f_lock:
                        try:
                            if not self.isFileExists(local_path):
                                with self.save_atomic(local_path) as local_tmp_path:
                                    logging.info("Download file from s3 to: %s, temp folder: %s"%(local_path, local_tmp_path))
                                    self.downloadFile(path, local_tmp_path)
                        finally:
                            f_lock.close()
                            self.removeFile(local_lock_path)
                    else:
                        self.waitForFile(local_path, True, num_tries=300, interval_sec=10)

                path_to_load = local_path
            else:
                with self.save_atomic(path, move_file=False) as local_tmp_path:
                    self.downloadFile(path, local_tmp_path)
                    return joblib.load(local_tmp_path)
        else:
            path_to_load = path

        return joblib.load(path_to_load)

    def loadNPObjectFromFile(self, path):
        import numpy as np

        if self.isS3Path(path):
            with self.save_atomic(path, move_file=False) as local_path:
                self.downloadFile(path, local_path)
                return np.load(local_path, allow_pickle=True)

        return np.load(path, allow_pickle=True)

    def _read_feather(self, path, features=None):
        from pyarrow import feather

        if path.endswith(".gz") or path.endswith(".zip"):
            with FSClient().open(path, 'rb', encoding=None) as local_file:
                return feather.read_feather(local_file, columns=features, use_threads=bool(True))

        return feather.read_feather(path, columns=features, use_threads=bool(True))

    def loadDBFromFeatherFile(self, path, features=None):
        if self.isS3Path(path):
            with self.save_atomic(path, move_file=False) as local_path:
                self.downloadFile(path, local_path)
                return self._read_feather(local_path, features)

        return self._read_feather(path, features)

    def _read_parquet(self, path, features=None):
        import pandas as pd

        return pd.read_parquet(path, columns=features)

    def loadDBFromParquetFile(self, path, features=None):
        if self.isS3Path(path):
            with self.save_atomic(path, move_file=False) as local_path:
                self.downloadFile(path, local_path)
                return self._read_parquet(local_path, features)

        return self._read_parquet(path, features)

    def isAbsPath(self, path):
        import platform

        if not path:
            return False

        if self.isS3Path(path):
            return True

        if path.startswith("http:") or path.startswith("https:"):
            return True

        if platform.system().lower() == 'windows':
            return ':\\' in path or ':/' in path

        return path[0] == "/" or path[0] == "\\"

    def merge_folder_files(self, path, remove_folder=True):
        if self.isFileExists(path):
            return

        res = os.path.splitext(path)
        path_no_ext = res[0]
        extension = res[1]
        if not self.isDirExists(path_no_ext):
            return

        client = self._getFSClientByPath(path)
        files = list(client.listFolder(path_no_ext))

        with FSClient().open(path, 'w') as file_output:
            for idx, file in enumerate(files):
                if file.endswith(extension):
                    with self.open(os.path.join(path_no_ext, file), 'rb') as file_input:
                        data_file = file_input.read()
                        if extension == ".json":
                            data_file = self._process_merged_json(data_file, idx, len(files))

                        file_output.write(data_file)

        if remove_folder:
            client.removeFolder(path_no_ext)

    @staticmethod
    def _process_merged_json(data_file, idx, total_len):
        remove_last = False
        remove_first = False

        if idx == 0:
            remove_last = True
        elif idx == total_len-1:
            remove_first = True
        else:
            remove_last = True
            remove_first = True

        if remove_last:
            index = data_file.rindex(']')
            if index >=0:
                data_file = data_file[:index] + "," + data_file[index + 1:]
        if remove_first:
            index = data_file.index('[')
            if index >=0:
                data_file = data_file[:index] + data_file[index + 1:]

        return data_file

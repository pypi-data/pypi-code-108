# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=line-too-long
# pylint: disable=bare-except
# pylint: disable=unused-import
"""
    Contains the general methods for manipulating files.
"""

# import json
# import shutil
# import time
# import json
# import re
# from pathlib import Path
import time
import json
from datetime import timezone
from datetime import datetime
import gzip
import os
import io
import shutil
import traceback
from threading import Thread
import logging

import ftputil
from secure_delete import secure_delete
import colemen_string_utils as strUtils
import utils.dir as directory
import utils.resources
# import utils.dir as dirUtils
# from utils.dir import create as create_dir
import utils.objectUtils as obj
import utils.file_read as read
import utils.file_write as write
import utils.file_search as search
import utils.file_convert as convert
import utils.file_image as image
# from utils.dir import get_folders_ftp
# import utils.string_utils as strUtils

logger = logging.getLogger(__name__)

PILLOW_SUPPORTED_IMAGE_EXTENSIONS = ["bmp","dds","dib","eps","gif","icns","ico","im","jpg","jpeg","jpeg 2000","msp","pcx","png","ppm","sgi","spider","tga","tiff","webp","xbm"]


def decompress(file_obj, compression="gzip"):
    '''
        Decompresses a file or list of files in place.

        ----------

        Arguments
        -------------------------
        `file_obj` {string|list}
            A file path or list of file_paths to decompress.

        [`compression`="gzip"] {string}
            The type of compression to use.

        Return {list}
        ----------------------
        A list of dictionaries [{file_path:"xx",content:"xx"},...]

        An empty list if nothing is found.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 12:08:44
        `memberOf`: file
        `version`: 1.0
        `method_name`: decompress
    '''
    file_list = gen_path_list(file_obj)
    result_list = []
    if len(file_list) > 0:
        for file in file_list:
            if compression == "gzip":
                data = {
                    "file_path": file,
                    "contents": _decompress_single_file_gzip(file)
                }
                result_list.append(data)
    return result_list


def compress(file_obj):
    '''
        gzip Compress the file provided.

        ----------

        Arguments
        -------------------------
        `file_obj` {str|list|dict}
            It can be a single path, list of paths, list of file objects, or a single file object.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 14:00:20
        `memberOf`: file
        `version`: 1.0
        `method_name`: compress
    '''
    file_list = gen_path_list(file_obj)
    if len(file_list) > 0:
        for file_path in file_list:
            _compress_single_file_gzip(file_path)


def _decompress_single_file_gzip(file_path):
    temp_path = strUtils.format.file_path(f"{os.path.dirname(file_path)}/{get_name_no_ext(file_path)}.decomp")
    contents = False
    try:
        with gzip.open(file_path, 'rb') as file:
            with io.TextIOWrapper(file, encoding='utf-8') as decoder:
                contents = decoder.read()
                write.write(temp_path, contents)
    except gzip.BadGzipFile:
        print(f"File is not compressed: {file_path}")
        contents = read.read(file_path)

    if contents is not False:
        # delete the compressed file
        delete(file_path)
        # rename the decompressed file
        rename(temp_path, file_path)
    return contents


def _compress_single_file_gzip(file_path):
    success = False
    try:
        contents = read.read(file_path)
        with gzip.open(file_path, 'wb') as target_file:
            target_file.write(contents.encode())
            success = True
    except OSError as error:
        print(f"Failed to compress: {file_path} \n{error}")
        print(traceback.format_exc())
    return success


def exists(file_path, **kwargs):
    '''
        Confirms that the file exists.

        Arguments
        ----------
        `file_path` {str}
            The file path to test.

        Keyword Arguments
        -------------------------
        [`ftp`=None] {bool}
            A reference to the ftputil object to use.


        ----------
        `return` {bool}
            True if the file exists, False otherwise.


        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-17-2021 17:15:22
        `memberOf`: file
        `version`: 1.1
        `method_name`: exists


        Changes
        ----------
        12\\17\\2021 17:16:04 - 1.1 - typo on isFile function call.
    '''

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is not None:
        if ftp.path.isfile(file_path):
            if ftp.path.exists(file_path):
                return True
        return False

    if os.path.isfile(file_path) is True:
        return True
    else:
        return False


def delete(file_path, **kwargs):
    '''
        Deletes a file

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The path to the file that will be deleted.

        Keyword Arguments
        -------------------------
        [`shred`=False] {bool}
            if True, the file is shredded and securely deleted.
        [`ftp`=None] {object}
            A reference to the ftputil object to use.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-09-2021 12:12:08
        `memberOf`: file
        `version`: 1.0
        `method_name`: delete
    '''
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    shred = obj.get_kwarg(["shred", "secure"], False, (bool), **kwargs)
    threading = obj.get_kwarg(["threading"], True, (bool), **kwargs)
    max_threads = obj.get_kwarg(["max_threads"], 15, (int), **kwargs)
    min_thread_threshold = obj.get_kwarg(["min thread threshold", "min files thread"], 100, (int), **kwargs)

    file_list = gen_path_list(file_path)
    # print("file_list: ", json.dumps(file_list, indent=4))
    # exit()
    if len(file_list) > 0:
        if threading is True and len(file_list) >= min_thread_threshold and ftp is None:
            _thread_file_action(file_list, action="delete", max_threads=max_threads, min_thread_threshold=min_thread_threshold, shred=shred, ftp=ftp)
            return

        for file in file_list:
            if isinstance(file, (dict)):
                if 'file_path' in file:
                    _delete_single_file(file['file_path'], shred, ftp)
            if isinstance(file, (str)):
                # print(f"_delete_single_file")
                _delete_single_file(file, shred, ftp)
    return True


def gen_path_list(file_obj):
    '''
        Generates a list of file paths from the mixed type object provided.

        ----------

        Arguments
        -------------------------
        `file_obj` {str|list|dict}
            The object to parse for file_paths.

            It can be a single path, list of paths, list of file objects, or a single file object.

        Return {list}
        ----------------------
        A list of file paths, if none are found, the list is empty.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-10-2021 10:08:53
        `memberOf`: file
        `version`: 1.0
        `method_name`: gen_path_list
    '''
    file_list = []

    if isinstance(file_obj, (str)) is True:
        file_list.append(file_obj)

    if isinstance(file_obj, (list)) is True:
        for file in file_obj:
            if isinstance(file, (str)) is True:
                file_list.append(file)
            if isinstance(file, (dict)) is True:
                if "file_path" in file:
                    file_list.append(file["file_path"])

    if isinstance(file_obj, (dict)) is True:
        if "file_path" in file_obj:
            file_list.append(file_obj["file_path"])
    return file_list


def import_project_settings(file_name):
    '''
        Used to import a json file, same as just reading a json file.
        It only searches the working directory for a json file with a matching name.
        Kept for backward compatibility.

        ----------

        Arguments
        -------------------------
        `file_name` {str}
            The name of the settings file to search for and import.


        Return {mixed}
        ----------------------
        The json decoded file.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 14:02:53
        `memberOf`: file
        `version`: 1.0
        `method_name`: import_project_settings
    '''
    settings_path = file_name
    if exists(settings_path) is False:
        settings_path = search.by_name(file_name, os.getcwd(), exact_match=False)
        if settings_path is False:
            return False
    return read.as_json(settings_path)


def _parse_copy_data_from_obj(file_obj):
    data = {
        "src_path": None,
        "dst_path": None,
    }
    if isinstance(file_obj, (tuple, list)):
        if len(file_obj) == 2:
            data['src_path'] = file_obj[0]
            data['dst_path'] = file_obj[1]
        else:
            print("Invalid list/tuple provided for copy file. Must be [source_file_path, destination_file_path]")
    if isinstance(file_obj, (dict)):
        for syn in utils.resources.SRC_PATH_SYNONYMS:
            synvar = strUtils.gen.variations(syn)
            for synonym_variant in synvar:
                if synonym_variant in file_obj:
                    data['src_path'] = file_obj[synonym_variant]
        for syn in utils.resources.DEST_PATH_SYNONYMS:
            synvar = strUtils.gen.variations(syn)
            for synonym_variant in synvar:
                if synonym_variant in file_obj:
                    data['dst_path'] = file_obj[synonym_variant]

    if exists(data['src_path']) is False:
        print(f"Invalid source path provided, {data['src_path']} could not be found.")
    return data


def rename(src_path, dst_path, ftp=None):
    '''
        Rename a file on the local machine or on an FTP server.

        ----------

        Arguments
        -------------------------
        `src_path` {str}
            The path to the file to rename
        `dst_path` {str}
            The new path for the file.
        [`ftp`=None] {object}
            A reference to the ftputil object to use.


        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-17-2021 16:47:49
        `memberOf`: file
        `version`: 1.0
        `method_name`: rename
    '''
    if ftp is not None:
        ftp.rename(src_path, dst_path)
        return True
    success = False
    if exists(src_path):
        os.rename(src_path, dst_path)
        success = True
    return success


def copy(src, dest=False, **kwargs):
    '''
        Copy a file from one location to another

        ----------

        Arguments
        -------------------------
        `src` {string|list|tuple|dict}
            The path to the file that will be copied.

            if it is a list/tuple:
                [src_path,dst_path]

                or nested lists [one level max.]

                [[src_path,dst_path],[src_path,dst_path]]

                or a list of dictionaries, lists and/or tuples

                [{src_path:"xx",dst_path:"xx"},[src_path,dst_path]]

            if it is a dictionary:
                The dictionary must have at least one of these keys or variation of it:

                ["source", "src", "src path", "source path", "file path"]

                ["dest", "dst", "dest path", "destination", "destination path", "dst path", "target", "target path"]


        [`src`=False] {string}
            Where to copy the source file to.

            if False, it is assumed that the src is a list,tuple, or dictionary.

        Keyword Arguments
        -------------------------
        [`threading`=True] {bool}
            If True, and there are more files than "min_thread_threshold", then the copy task is divided into threads.

            If False, the files are copied one at a time.

        [`max_threads`=15] {int}
            The total number of threads allowed to function simultaneously.

        [`min_thread_threshold`=100] {int}
            There must be this many files to copy before threading is allowed.

        [`ftp`=None] {object}
            A reference to the ftputil object to use.

        [`ftp_credentials`=None] {object}
            If threading is True and it is an ftp copy, you must provide ftp credentials.

        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-09-2021 12:39:45
        `memberOf`: file
        `version`: 1.0
        `method_name`: copy
    '''
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    ftp_credentials = obj.get_kwarg(["ftp_credentials"], None, None, **kwargs)
    threading = obj.get_kwarg(["threading"], True, (bool), **kwargs)
    max_threads = obj.get_kwarg(["max_threads"], 15, (int), **kwargs)
    min_thread_threshold = obj.get_kwarg(["min thread threshold", "min files thread"], 100, (int), **kwargs)

    copy_list = []
    if dest is False:
        if isinstance(src, (list, tuple, dict)):
            if isinstance(src, (list, tuple)):
                for item in src:
                    copy_obj = _parse_copy_data_from_obj(item)
                    if copy_obj['src_path'] is not None and copy_obj['dst_path'] is not None:
                        copy_list.append(_parse_copy_data_from_obj(item))
            if isinstance(src, (dict)):
                copy_obj = _parse_copy_data_from_obj(src)
                if copy_obj['src_path'] is not None and copy_obj['dst_path'] is not None:
                    copy_list.append(_parse_copy_data_from_obj(src))
    else:
        copy_obj = _parse_copy_data_from_obj([src, dest])
        copy_list.append(copy_obj)

    if threading is True:
        if len(copy_list) >= min_thread_threshold:
            if ftp_credentials is not None:
                _thread_file_action(copy_list, action="copy", max_threads=max_threads, min_thread_threshold=min_thread_threshold, ftp=ftp, ftp_credentials=ftp_credentials)
                return
            else:
                _thread_file_action(copy_list, action="copy", max_threads=max_threads, min_thread_threshold=min_thread_threshold)
            return

    _copy_files_from_array(copy_list, ftp)
    # print(f"copy_list: {copy_list}")


def _copy_files_from_array(file_list, ftp=None, attempted_delete=False):
    for file in file_list:
        try:
            if ftp is not None:
                directory.create(os.path.dirname(file['dst_path']), False, ftp=ftp)
                ftp.upload_if_newer(file['src_path'], file['dst_path'])
                continue

            os.makedirs(os.path.dirname(file['dst_path']), exist_ok=True)
            shutil.copy2(file['src_path'], file['dst_path'])
        except PermissionError as error:
            if attempted_delete is False:
                _delete_single_file(file['dst_path'])
                _copy_files_from_array([file], ftp, True)
            else:
                print(f"Failed to copy file: {file['src_path']} to {file['dst_path']}.\n{error}")
                print(traceback.format_exc())
    return True


def _delete_single_file(file_path, shred=False, ftp=None):
    '''
        Deletes or shreds a single file.

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            Path to the file to delete.
        [`shred`=False] {bool}
            Securely shred the file (slower)
        [`ftp`=None] {object}
            A reference to the ftputil object to use.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-10-2021 10:18:06
        `memberOf`: file
        `version`: 1.0
        `method_name`: _delete_single_file
    '''
    success = False
    if ftp is not None:
        # print(f"file.delete.file_path: {file_path}")
        if exists(file_path, ftp=ftp) is True:
            ftp.remove(file_path)
    else:
        if exists(file_path) is True:
            try:
                if shred is True:
                    secure_delete.secure_random_seed_init()
                    secure_delete.secure_delete(file_path)
                else:
                    os.remove(file_path)
            except PermissionError as error:
                print(f"Failed to delete {file_path}, {error}")
                success = True
        else:
            success = True

    if exists(file_path) is False:
        success = False
    return success


def _delete_files_from_array(file_list, shred=False, ftp=None):
    '''
        Delete a list of files.

        ----------

        Arguments
        -------------------------
        `file_list` {list}
            A list of file paths to delete.

        [`shred`=False] {bool}
            Securely shred and delete the files (slower.)

        Return {bool}
        ----------------------
        True if ALL files are deleted, False if any fail.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-10-2021 10:19:44
        `memberOf`: file
        `version`: 1.0
        `method_name`: _delete_files_from_array
    '''
    success = True
    for file in file_list:
        if exists(file, ftp=ftp):
            result = _delete_single_file(file, shred=shred, ftp=None)
            if result is not True:
                success = False
    return success


def _thread_file_action(file_list, **kwargs):
    max_threads = obj.get_kwarg(["max_threads"], 15, (int), **kwargs)
    min_thread_threshold = obj.get_kwarg(["min thread threshold", "min files thread"], 100, (int), **kwargs)
    action = obj.get_kwarg(["action"], "copy", (str), **kwargs)
    shred = obj.get_kwarg(["shred"], False, (bool), **kwargs)
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    ftp_credentials = obj.get_kwarg(["ftp_credentials"], None, None, **kwargs)

    if len(file_list) <= min_thread_threshold:
        max_threads = 1

    files_per_thread = round(len(file_list) / max_threads)
    threads = []
    for idx in range(max_threads):
        start_idx = files_per_thread * idx
        end_idx = start_idx + files_per_thread
        if end_idx > len(file_list):
            end_idx = len(file_list)
        files_array = file_list[start_idx:end_idx]
        
        if action == "copy":
            if ftp_credentials is not None:
                ftp = ftputil.FTPHost(ftp_credentials['address'], ftp_credentials['user_name'], ftp_credentials['password'])
                ftp.synchronize_times()
                threads.append(Thread(target=_copy_files_from_array, args=(files_array,ftp)))
                continue
            threads.append(Thread(target=_copy_files_from_array, args=(files_array,ftp)))
        if action == "delete":
            threads.append(Thread(target=_delete_files_from_array, args=(files_array, shred, ftp)))

    if action == "copy":
        print(f"    Copying {len(file_list)} files.")
    if action == "delete":
        print(f"    Deleting {len(file_list)} files.")
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return


def get_data(file_path, **kwargs):
    '''
        Get data associated to the file_path provided.

        ----------

        Arguments
        -----------------
        `file_path`=cwd {str}
            The path to the file.

        Keyword Arguments
        -----------------

            `include`=[] {list}
                A list of keys to include in the returning dictionary.
                This is primarily useful for limiting the time/size of the operation.

            [`ftp`=None] {object}
                A reference to the ftputil object to use.

        Return
        ----------
        `return` {str}
            A dictionary containing the file's data.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 11:02:09
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_data
    '''
    ftp = obj.get_kwarg(['ftp'], None, None, **kwargs)
    if ftp is not None:
        file_data = {}
        path = strUtils.format.file_path(file_path, url=True)
        # print(f"file.get_data.path:{path}")
        # print(f"ftp: {ftp.path}")
        lstat = ftp.lstat(path)
        file_data['file_path'] = path
        file_data['file_name'] = ftp.path.basename(path)
        file_data['extension'] = get_ext(path)
        file_data['name_no_ext'] = get_name_no_ext(file_path)
        file_data['dir_path'] = ftp.path.dirname(file_path)
        file_data['modified_time'] = datetime.timestamp(datetime.utcfromtimestamp(lstat[8]))
        file_data['size'] = lstat[6]
        return file_data

    data_include = obj.get_kwarg(['include', "data include"], [], (list, str), **kwargs)
    if isinstance(data_include, (str)):
        data_include = [data_include]
    if len(data_include) == 0:
        data_include = ['file_name', 'extension', 'name_no_ext', 'dir_path', 'access_time', 'modified_time', 'created_time', 'size']
    file_path = strUtils.format.file_path(file_path)
    if exists(file_path):
        # print(f"file exists: {file_path}")
        # print(f"Getting data for file: {file_path}")
        try:
            file_data = {}
            file_data['file_path'] = file_path

            if 'file_name' in data_include:
                file_data['file_name'] = os.path.basename(file_path)
            if 'extension' in data_include:
                file_data['extension'] = get_ext(file_path)
            if 'name_no_ext' in data_include:
                file_data['name_no_ext'] = get_name_no_ext(file_path)
            if 'dir_path' in data_include:
                file_data['dir_path'] = os.path.dirname(file_path)
            if 'access_time' in data_include:
                file_data['access_time'] = get_access_time(file_path)
            if 'modified_time' in data_include:
                file_data['modified_time'] = get_modified_time(file_path)
            if 'created_time' in data_include:
                file_data['created_time'] = get_create_time(file_path)
            if 'size' in data_include:
                file_data['size'] = os.path.getsize(file_path)

            return file_data
        except FileNotFoundError as error:
            logger.warning("Error: %s", error)
            return None
    else:
        logger.warning("Failed to find the file: %s", file_path)


def get_modified_time(file_path, ftp=None):
    '''
        get the modified from the file

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The file to get the modified time from.

        Return {int}
        ----------------------
        The timestamp formatted and rounded.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 10:45:32
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_modified_time
    '''
    if ftp is not None:
        return int(datetime.timestamp(datetime.utcfromtimestamp(ftp.path.getmtime(file_path))))

    mod_time = os.path.getmtime(file_path)
    mod_time = int(datetime.fromtimestamp(mod_time).replace(tzinfo=timezone.utc).timestamp())
    return int(datetime.timestamp(datetime.fromtimestamp(mod_time)))


def get_access_time(file_path):
    '''
        get the access from the file

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The file to get the access time from.

        Return {int}
        ----------------------
        The timestamp formatted and rounded.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 10:45:32
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_modified_time
    '''
    mod_time = os.path.getatime(file_path)
    return int(datetime.fromtimestamp(mod_time).replace(tzinfo=timezone.utc).timestamp())


def get_create_time(file_path):
    '''
        get the create from the file

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The file to get the create time from.

        Return {int}
        ----------------------
        The timestamp formatted and rounded.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 10:45:32
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_modified_time
    '''
    mod_time = os.path.getctime(file_path)
    return int(datetime.fromtimestamp(mod_time).replace(tzinfo=timezone.utc).timestamp())


def get_ext(file_path):
    '''
        Get the extension from the file path provided.

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The file path to be parsed.

        Return {string|boolean}
        ----------------------
        The extension of the file, if it can be parsed, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 10:40:21
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_ext
    '''
    file_name = os.path.basename(file_path)
    file_extension = False
    ext = os.path.splitext(file_name)
    if len(ext) == 2:
        file_extension = ext[1]
    return file_extension


def get_name_no_ext(file_path):
    '''
        Get the file name without an extension.

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The file path to be parsed.

        Return {type}
        ----------------------
        The file name without the extension

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-13-2021 10:38:44
        `memberOf`: file
        `version`: 1.0
        `method_name`: get_name_no_ext
    '''
    return os.path.basename(file_path).replace(get_ext(file_path), '')


def gen_relative_path(src_base, dst_base, file_path):
    '''
        Finds the relative path from the src_base, dst_base and file path.

        example:
            file_path = r"Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php\\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php"\n
            src_base = r"Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php"\n
            dst_base = r"/equari_php/\n
            relative_path = \\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php

        ----------

        Arguments
        -------------------------
        `src_base` {str}
            The path to the root directory of the "source".
        `dst_base` {str}
            The path to the root directory of the "destination".
        `file_path` {str}
            The path of the file to generate a relative path for.

        Return {string|None}
        ----------------------
        The relative path or None if one cannot be found.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-17-2021 16:14:55
        `memberOf`: file
        `version`: 1.1
        `method_name`: gen_relative_path

        Changes
        ----------
        12\\17\\2021 17:11:09 -If no path is provided, the file name is returned.
    '''
    src_base = strUtils.format.file_path(src_base)
    dst_base = strUtils.format.file_path(dst_base)
    file_path = strUtils.format.file_path(file_path)

    src_len = len(src_base)
    dst_len = len(dst_base)
    relative_path = None

    if src_base == dst_base:
        print("src_base is identical to dst_base")
        return relative_path

    if src_base not in file_path and dst_base not in file_path:
        print("The file path must originate from either the src_path or dst_path.")
        return relative_path

    if src_base in file_path:
        relative_path = file_path.replace(dst_base, "")
    if dst_base in file_path:
        relative_path = file_path.replace(dst_base, "")

    if src_len > dst_len:
        dst_pos = file_path.lower().find(dst_base.lower())
        if dst_pos != -1:
            # print(f"file originates from dst_base: {dst_pos}")
            if dst_pos == 0:
                relative_path = file_path[len(dst_base):]
            else:
                relative_path = file_path[dst_pos:]

            # print(f"relative_path: {file_path[dst_pos:]}")

    if dst_len > src_len:
        src_pos = file_path.lower().find(src_base.lower())
        if src_pos != -1:
            # print(f"file originates from src_base: {src_pos}")
            if src_pos == 0:
                relative_path = file_path[len(src_base):]
            else:
                relative_path = file_path[src_pos:]

    if relative_path is not None:
        relative_path = relative_path.replace(dst_base, "")
        relative_path = relative_path.replace(src_base, "")
    if relative_path is None:
        relative_path = os.path.basename(file_path)
        # print(f"boobs: {relative_path}")
    return relative_path


def gen_dst_path(src_base, dst_base, file_path):
    '''
        Generates the destination path for a file.


        example:
            file_path = r"Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php\\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php"\n
            src_base = r"Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php"\n
            dst_base = r"/equari_php/\n
            returns:\n
            \\equari_php\\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php

        ----------

        Arguments
        -------------------------
        `src_base` {str}
            The path to the root directory of the "source".
        `dst_base` {str}
            The path to the root directory of the "destination".
        `file_path` {str}
            The path of the file to generate a relative path for.

        Return {string|None}
        ----------------------
        The destination path to the file or None if one cannot be found.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-17-2021 16:21:22
        `memberOf`: file
        `version`: 1.0
        `method_name`: gen_dst_path
    '''
    src_base = strUtils.format.file_path(src_base)
    dst_base = strUtils.format.file_path(dst_base)
    file_path = strUtils.format.file_path(file_path)
    if src_base not in file_path and dst_base not in file_path:
        # print(f"tatertots")
        return strUtils.format.file_path(f"{dst_base}/{file_path}")
    relative_path = gen_relative_path(src_base, dst_base, file_path)
    return strUtils.format.file_path(f"{dst_base}/{relative_path}")


def gen_src_path(src_base, dst_base, file_path):
    '''
        Generates the source path for a file.


        example:
            src_base = r"Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php"\n
            dst_base = r"/equari_php/"\n
            file_path = r"\\equari_php\\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php"\n
            returns:\n
            Z:\\Structure\\Ra9\\2021\\21-0134_EquariServer\\equari_php\\equari_php\\pcom\\animal\\read\\PCOM_getOMNIAnimalData.php

        ----------

        Arguments
        -------------------------
        `src_base` {str}
            The path to the root directory of the "source".
        `dst_base` {str}
            The path to the root directory of the "destination".
        `file_path` {str}
            The path of the file to generate a relative path for.

        Return {string|None}
        ----------------------
        The source path to the file or None if one cannot be found.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-17-2021 16:21:22
        `memberOf`: file
        `version`: 1.0
        `method_name`: gen_dst_path
    '''
    src_base = strUtils.format.file_path(src_base)
    dst_base = strUtils.format.file_path(dst_base)
    file_path = strUtils.format.file_path(file_path)
    if src_base not in file_path and dst_base not in file_path:
        return strUtils.format.file_path(f"{src_base}/{file_path}")
    relative_path = gen_relative_path(src_base, dst_base, file_path)
    return strUtils.format.file_path(f"{src_base}/{relative_path}")


def get_files(search_path=False, **kwargs):
    '''
        Get all files/data from the search_path.

        ----------

        Keyword Arguments
        -----------------
            [`search_path`=cwd] {str|list}
                The search path or list of paths to iterate.

            [`recursive`=True] {boolean}
                If True the path is iterated recursively

            [`ignore`=[]] {str|list}
                A term or list or terms to ignore if the file path contains any of them.

            [`extensions|ext|extension`=[]] {str|list}
                An extension or list of extensions that the file must have.\n
                Can have leading periods or not.\n
                if equal to "images" it will automatically search for these extensions:
                    bmp,dds,dib,eps,gif,icns,ico,im,jpg,jpeg,jpeg 2000,msp,pcx,png,ppm,sgi,spider,tga,tiff,webp,xbm

            [`threaded`=True] {bool}
                if True, the process is multi-threaded,
                this makes indexing much faster,
                but it can easily overwhelm a cpu depending upon the drive.

            `data_include` {str|list}
                The data to get for each file, the shorter this list the faster it will complete.
                By default it will get this:
                    ['file_name', 'extension', 'name_no_ext', 'dir_path', 'access_time',
                    'modified_time', 'created_time', 'size']
                so the list you provide will limit the amount of
                reading/formatting needed to gather data.
                Example:
                    ['modified_time','size']  will take ~0.000129939 seconds per file on an SSD

                    ['file_name', 'extension', 'name_no_ext', 'dir_path', 'access_time',
                    'modified_time', 'created_time', 'size']

                    will take ~0.000173600 seconds per file on an SSD,
                    it's not much but little things matter.. that's what she said.

            [`ftp`=None] {obj}
                A reference to the ftputil object.

        return
        ----------
        `return` {list}
            A list of dictionaries containing all matching files.
    '''
    file_array = []

    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]

    threaded = obj.get_kwarg(['threaded', 'thread'], True, bool, **kwargs)
    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

    data_include = obj.get_kwarg(['data include'], [], (list, str), **kwargs)
    if isinstance(data_include, (str)):
        data_include = [data_include]

    # ignore_array = obj.get_kwarg(['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    extension_array = strUtils.format.extension(obj.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs))
    extension_array = _gen_extension_array(extension_array)
            

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is not None:
        return get_files_ftp(search_path, **kwargs)

    if threaded is True:
        for path in search_path:
            gft = GetFilesThreaded(path, recursive=recursive, data_include=data_include, exclude=exclude, include=include, extensions=extension_array)
            return gft.master()
    # print(json.dumps(extension_array, indent=4))
    for path in search_path:
        path = strUtils.format.file_path(path)
        # pylint: disable=unused-variable
        for root, folders, files in os.walk(path):
            for file in files:
                file_data = get_data(os.path.join(root, file), include=data_include)
                if file_data is not None:
                    # ignore = False
                    # print(f"file_data['extension']: {file_data['extension']}")
                    if len(exclude) > 0:
                        # print(f"filtering excludes")
                        if strUtils.parse.array_in_string(exclude, file_data['file_path']) is True:
                            continue

                    if len(include) > 0:
                        # print(f"filtering includes")
                        if strUtils.parse.array_in_string(include, file_data['file_path']) is False:
                            continue

                    if len(extension_array) > 0:
                        # print(f"filtering extension_array")
                        file_ext = strUtils.format.extension(file['extension'])
                        if file_ext not in extension_array:
                            continue

                    # if len(ignore_array) > 0:
                    #     for ignore_string in ignore_array:
                    #         if ignore_string in file_data['file_path']:
                    #             ignore = True

                    # if ignore is False:
                        # fd['file_hash'] = generateFileHash(fd['file_path'])
                    # print(f"file found.")
                    file_array.append(file_data)
                # else:
                    # print(f"file_data is none")
            if recursive is False:
                # print(f"breaking")
                break

        # path_files = index_files(path, extension_array, ignore_array, recursive)
        # file_array = path_files + file_array
    return file_array

def _gen_extension_array(ext_array):
    extension_array = []
    if isinstance(ext_array, (str)):
        extension_array = [ext_array]
    for ext in extension_array:
        if ext == "images":
            extension_array = extension_array + PILLOW_SUPPORTED_IMAGE_EXTENSIONS
        else:
            file_ext = strUtils.format.extension(ext)
            extension_array.append(file_ext)
    return extension_array

def get_files_ftp(search_path=False, **kwargs):
    '''
        Get all files/data from the search_path.

        ----------

        Keyword Arguments
        -----------------
            `ftp` {obj}
                A reference to the ftputil object.        
            [`search_path`=cwd] {str|list}
                The search path or list of paths to iterate.

            [`recursive`=True] {boolean}
                If True the path is iterated recursively

            [`ignore`=[]] {str|list}
                A term or list or terms to ignore if the file path contains any of them.

            [`extensions`=[]] {str|list}
                An extension or list of extensions that the file must have.

            `data_include` {str|list}
                The data to get for each file, the shorter this list the faster it will complete.
                By default it will get this:
                    ['file_name', 'extension', 'name_no_ext', 'dir_path', 'access_time',
                    'modified_time', 'created_time', 'size']
                so the list you provide will limit the amount of
                reading/formatting needed to gather data.
                Example:
                    ['modified_time','size']  will take ~0.000129939 seconds per file on an SSD

                    ['file_name', 'extension', 'name_no_ext', 'dir_path', 'access_time',
                    'modified_time', 'created_time', 'size']

                    will take ~0.000173600 seconds per file on an SSD,
                    it's not much but little things matter.. that's what she said.



        return
        ----------
        `return` {list}
            A list of dictionaries containing all matching files.
    '''
    file_array = []
    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]

    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

    data_include = obj.get_kwarg(['data include'], [], (list, str), **kwargs)
    if isinstance(data_include, (str)):
        data_include = [data_include]

    # ignore_array = obj.get_kwarg(['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    extension_array = strUtils.format.extension(
        obj.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs))
    if isinstance(extension_array, (str)):
        extension_array = [extension_array]

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is None:
        logger.warning("No FTP obj reference provided.")
        return False

    for path in search_path:
        # pylint: disable=unused-variable
        for root, folders, files in ftp.walk(path):
            for file in files:
                file_path = strUtils.format.file_path(os.path.join(root, file), url=True)
                file_data = get_data(file_path, include=data_include, ftp=ftp)
                if file_data is not None:
                    # ignore = False
                    # print(f"file_data['extension']: {file_data['extension']}")
                    if len(exclude) > 0:
                        if strUtils.parse.array_in_string(exclude, file_data['file_path']) is True:
                            continue

                    if len(include) > 0:
                        if strUtils.parse.array_in_string(include, file_data['file_path']) is False:
                            continue

                    if len(extension_array) > 0:
                        file_ext = strUtils.format.extension(file_data['extension'])
                        if file_ext not in extension_array:
                            continue

                    # if len(ignore_array) > 0:
                    #     for ignore_string in ignore_array:
                    #         if ignore_string in file_data['file_path']:
                    #             ignore = True

                    # if ignore is False:
                        # fd['file_hash'] = generateFileHash(fd['file_path'])
                    file_array.append(file_data)

            if recursive is False:
                break
        return file_array
        # path_files = index_files(path, extension_array, ignore_array, recursive)
        # file_array = path_files + file_array
    return file_array


class GetFilesThreaded:
    '''
        A class implementation of the get_files method.
        This allows it use threading.
    '''

    def __init__(self, search_path, **kwargs):
        self.threads = []
        self.thread_array = []
        self.file_array = []
        self.max_threads = 20
        self.search_path = search_path

        if search_path is False:
            self.search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
        if isinstance(self.search_path, list) is False:
            self.search_path = [self.search_path]

        self.recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

        self.data_include = obj.get_kwarg(['data include'], [], (list, str), **kwargs)
        if isinstance(self.data_include, (str)):
            self.data_include = [self.data_include]

        # ignore_array = obj.get_kwarg(
            # ['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
        self.exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
        if isinstance(self.exclude, (str)):
            self.exclude = [self.exclude]

        self.include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
        if isinstance(self.include, (str)):
            self.include = [self.include]

        self.extension_array = strUtils.format.extension(
            obj.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs))
        if isinstance(self.extension_array, (str)):
            self.extension_array = [self.extension_array]

    def remove_thread_by_id(self, thread_id):
        '''
            Removes an active thread from self.threads

            ----------

            Arguments
            -------------------------
            `thread_id` {str}
                The id of the thread to remove

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 12-19-2021 13:48:58
            `memberOf`: dir
            `version`: 1.0
            `method_name`: remove_thread_by_id
        '''
        threads = self.threads
        new_threads = []
        for thread in threads:
            if thread != thread_id:
                new_threads.append(thread)
        self.threads = new_threads

    def _get_data_thread(self, file_path):
        file_data = get_data(file_path, data_include=self.data_include)
        if file_data is not None:
            # ignore = False
            # print(f"file_data['extension']: {file_data['extension']}")
            if len(self.exclude) > 0:
                if strUtils.parse.array_in_string(self.exclude, file_data['file_path']) is True:
                    return

            if len(self.include) > 0:
                if strUtils.parse.array_in_string(self.include, file_data['file_path']) is False:
                    return

            if len(self.extension_array) > 0:
                file_ext = strUtils.format.extension(file_data['extension'])
                if file_ext not in self.extension_array:
                    return

        self.file_array.append(file_data)

    def single_file_thread(self, data):
        '''
            Executes the get_data function on an array of files in a separate thread
            and removes itself from self.threads once completed.

            ----------

            Arguments
            -------------------------
            `data` {dict}
                a dictionary containing the file_paths and thread_id keys

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 12-19-2021 13:49:59
            `memberOf`: dir
            `version`: 1.0
            `method_name`: single_file_thread
        '''
        file_paths = data['file_paths']
        for file_path in file_paths:
            self._get_data_thread(file_path)
        self.remove_thread_by_id(data['thread_id'])

    def master(self):
        '''
            Executes the get files process using threads

            ----------

            Return {list}
            ----------------------
            A list of files found in the search_path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 12-19-2021 13:52:24
            `memberOf`: dir
            `version`: 1.0
            `method_name`: master
        '''
        for path in self.search_path:
            # pylint: disable=unused-variable
            for root, folders, files in os.walk(path):

                # print(f"Active Threads: {strUtils.format.left_pad(len(self.threads),3,'0')} Total Files: {len(self.file_array)}", end="\r", flush=True)
                while len(self.threads) >= self.max_threads:
                    time.sleep(.1)

                file_paths = [os.path.join(root, x) for x in files]
                data = {
                    "thread_id": strUtils.gen.hash(json.dumps(file_paths)),
                    "file_paths": file_paths
                }
                thread = Thread(target=self.single_file_thread, args=(data,))
                self.threads.append(data['thread_id'])
                self.thread_array.append(thread)
                thread.start()

                if self.recursive is False:
                    break
            # return self.file_array
            # path_files = index_files(path, extension_array, ignore_array, recursive)
            # file_array = path_files + file_array
        # print(f"                                                                                                                      ", end="\r", flush=True)
        for thread in self.thread_array:
            thread.join()
        return self.file_array

        # def _get_files_single_thread(search_path=False, recursive=False, exclude=None, include=None, extensions=None, data_include=None):
        #     '''
        #         Get all files/data from the search_path.

        #         ----------
        #         Keyword Arguments
        #         -----------------

        #             `search_path`=cwd {str|list}
        #                 The search path or list of paths to iterate.
        #             `recursive`=True {boolean}
        #                 If True the path is iterated recursively
        #             `ignore`=[] {str|list}
        #                 A term or list or terms to ignore if the file path contains any of them.
        #             `extensions`=[] {str|list}
        #                 An extension or list of extensions that the file must have.

        #         return
        #         ----------
        #         `return` {str}
        #             A list of dictionaries containing all matching files.
        #     '''
        #     global _THREAD_GET_FILES_ARRAY
        #     if exclude is None:
        #         exclude = []
        #     if include is None:
        #         include = []
        #     if extensions is None:
        #         extensions = []
        #     if data_include is None:
        #         data_include = []
        #     for path in search_path:
        #         print(f"Files indexed: {len(_THREAD_GET_FILES_ARRAY)}", end="\r", flush=True)
        #         _THREAD_GET_FILES_ARRAY = _THREAD_GET_FILES_ARRAY + get_files(search_path=path, recursive=recursive, exclude=exclude, include=include, extensions=extensions, data_include=data_include)
        #     # _THREAD_GET_FILES_ARRAY = _THREAD_GET_FILES_ARRAY + get_files(search_path=search_path, recursive=recursive, exclude=exclude, include=include, extensions=extensions)
        #     return

        # def get_files_thread(search_path=False, **kwargs):
        #     '''
        #         Get all files/data from the search_path.

        #         ----------
        #         Keyword Arguments
        #         -----------------

        #             `search_path`=cwd {str|list}
        #                 The search path or list of paths to iterate.
        #             `recursive`=True {boolean}
        #                 If True the path is iterated recursively
        #             `ignore`=[] {str|list}
        #                 A term or list or terms to ignore if the file path contains any of them.
        #             `extensions`=[] {str|list}
        #                 An extension or list of extensions that the file must have.

        #         return
        #         ----------
        #         `return` {str}
        #             A list of dictionaries containing all matching files.
        #     '''
        #     global _THREAD_GET_FILES_ARRAY
        #     _THREAD_GET_FILES_ARRAY = []

        #     file_array = []
        #     if search_path is False:
        #         search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
        #     if isinstance(search_path, list) is False:
        #         search_path = [search_path]

        #     data_include = obj.get_kwarg(['data include'], [], (list, str), **kwargs)
        #     if isinstance(data_include, (str)):
        #         data_include = [data_include]

        #     recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

        #     # ignore_array = obj.get_kwarg(['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
        #     exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
        #     if isinstance(exclude, (str)):
        #         exclude = [exclude]

        #     include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
        #     if isinstance(include, (str)):
        #         include = [include]

        #     extension_array = strUtils.format.extension(obj.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs))
        #     if isinstance(extension_array, (str)):
        #         extension_array = [extension_array]

        #     dir_array = get_folders(search_path, recursive=recursive, exclude=exclude, include=include, paths_only=True)
        #     # dir_array.append(search_path)
        #     max_threads = 30
        #     dirs_per_thread = round(len(dir_array) / max_threads)
        #     print(f"dirs_per_thread: {dirs_per_thread}")
        #     threads = []
        #     for idx in range(max_threads):
        #         min_id = idx * dirs_per_thread
        #         max_id = min_id + dirs_per_thread
        #         if max_id > len(dir_array):
        #             max_id = len(dir_array)

        #         search_paths = dir_array[min_id:max_id]
        #         print(f"Thread {idx} [{min_id}:{max_id}]")
        #         threads.append(Thread(target=_get_files_single_thread, args=(search_paths, recursive, exclude, include, data_include)))

        #         # file_array = get_files(search_paths, recursive=recursive, exclude=exclude, include=include)
        #         # file_array += get_files(search_paths, recursive=recursive, exclude=exclude, include=include)
        #     for thread in threads:
        #         thread.start()
        #     for thread in threads:
        #         thread.join()
        #         # print(f"result: {result}")
        #     return _THREAD_GET_FILES_ARRAY
        #     # print(f"dir_array")
        #     # print(json.dumps(dir_array, indent=4))
        #     # print(f"_THREAD_GET_FILES_ARRAY")
        #     # print(json.dumps(_THREAD_GET_FILES_ARRAY, indent=4))

        #     # print(f"Total files indexed: {len(file_array)}")


# file = r"C:\Users\Colemen\Desktop\DAZDOW~1\poses\STANDI~1\IM0008~1\Content\People\GENESI~2\Poses\AEONSO~1\STANDI~1\LIMBSL~1\SC-WE'~2.DUF"
# file = r"C:\\Users\\Colemen\\Desktop\\DAZ DOWNLOADS\\poses\\Standing Conversation Poses for Genesis 8\\IM00083571-01_StandingConversationPosesforGenesis8\\Content\\People\\Genesis 8 Male\\Poses\\Aeon Soul\\Standing Conversation\\Limbs Legs\\SC-We're all in the same boat Legs-M Genesis 8 Male.duf"
# clean = clean_path(file)
# print(f"clean file path: {clean}")
# print(exists(clean))
# file = strUtils.format.file_path(file)
# get_data(file)


# src = r"C:/Users/Colemen/Desktop/TEST_FOLDER/Mnemosyne Tests/sourceDirectory/rendering"
# dst = r"/mnemosyne_sync_test"
# file_path = r"C:\Users\Colemen\Desktop\TEST_FOLDER\Mnemosyne Tests\sourceDirectory\rendering\test folder\20211030011919612.jpg"
# print("relative path: ", gen_relative_path(src, dst, file_path))
# print("destination path: ", gen_dst_path(src, dst, file_path))
# print("source path: ", gen_src_path(src, dst, file_path))
# _copy_files_from_array([{"src_path": src, "dst_path": dst}])

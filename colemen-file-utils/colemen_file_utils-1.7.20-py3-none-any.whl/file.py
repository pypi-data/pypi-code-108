"""
    Contains the general methods for manipulating files.
"""

# import json
# import shutil
from datetime import timezone
import time
from datetime import datetime
import gzip
import json
import os
import re
import io
import shutil
import traceback
# from pathlib import Path

import objectUtils as obj
import file_read as read
import file_write as write
import file_search as search
import string_utils as strUtils
from secure_delete import secure_delete
from threading import Thread
import colemen_string_utils as strUtils
import logging

logger = logging.getLogger(__name__)

# pylint: disable=line-too-long
DEST_PATH_SYNONYMS = ["dest", "dst", "dest path", "destination", "destination path", "dst path", "target", "target path"]
SRC_PATH_SYNONYMS = ["source", "src", "src path", "source path", "file path"]

# todo - DOCUMENTATION FOR METHODS

# // TODO:Get optional file access,create,modified formatting.


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
    file_list = _gen_path_list(file_obj)
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
    file_list = _gen_path_list(file_obj)
    if len(file_list) > 0:
        for file_path in file_list:
            _compress_single_file_gzip(file_path)


def _decompress_single_file_gzip(file_path):
    temp_path = strUtils.format.file_path(f"{os.path.dirname(file_path)}/{get_name_no_ext(file_path)}.decomp")
    contents = False
    try:
        with gzip.open(file_path, 'rb') as ip:
            with io.TextIOWrapper(ip, encoding='utf-8') as decoder:
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


def exists(file_path):
    '''
        Confirms that the file exists.

        ----------
        `file_path` {str}
            The file path to test.

        ----------
        `return` {bool}
            True if the file exists, False otherwise.
    '''
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
    shred = obj.get_kwarg(["shred", "secure"], False, (bool), **kwargs)
    threading = obj.get_kwarg(["threading"], True, (bool), **kwargs)
    max_threads = obj.get_kwarg(["max_threads"], 15, (int), **kwargs)
    min_thread_threshold = obj.get_kwarg(["min thread threshold", "min files thread"], 100, (int), **kwargs)

    file_list = _gen_path_list(file_path)
    print("file_list: ", json.dumps(file_list, indent=4))
    # exit()
    if len(file_list) > 0:
        if threading is True and len(file_list) >= min_thread_threshold:
            _thread_file_action(file_list, action="delete", max_threads=max_threads, min_thread_threshold=min_thread_threshold, shred=shred)
            return

        for file in file_list:
            if isinstance(file, (dict)):
                if 'file_path' in file:
                    _delete_single_file(file['file_path'], shred)
            if isinstance(file, (str)):
                _delete_single_file(file, shred)
    return True


def _gen_path_list(file_obj):
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
        `method_name`: _gen_path_list
    '''
    file_list = []

    if isinstance(file_obj, (str)) is True:
        if exists(file_obj):
            file_list.append(file_obj)

    if isinstance(file_obj, (list)) is True:
        for file in file_obj:
            if isinstance(file, (str)) is True:
                if exists(file):
                    file_list.append(file)
            if isinstance(file, (dict)) is True:
                if "file_path" in file:
                    if exists(file["file_path"]):
                        file_list.append(file["file_path"])

    if isinstance(file_obj, (dict)) is True:
        if "file_path" in file_obj:
            if exists(file_obj["file_path"]):
                file_list.append(file_obj["file_path"])
    return file_list


def import_project_settings(file_name):
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
            print(f"Invalid list/tuple provided for copy file. Must be [source_file_path, destination_file_path]")
    if isinstance(file_obj, (dict)):
        for syn in SRC_PATH_SYNONYMS:
            synvar = obj._gen_variations(syn)
            for sv in synvar:
                if sv in file_obj:
                    data['src_path'] = file_obj[sv]
        for syn in DEST_PATH_SYNONYMS:
            synvar = obj._gen_variations(syn)
            for sv in synvar:
                if sv in file_obj:
                    data['dst_path'] = file_obj[sv]

    if exists(data['src_path']) is False:
        print(f"Invalid source path provided, {data['src_path']} could not be found.")
    return data


def rename(src_path, dst_path):
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
                copy_obj = _parse_copy_data_from_obj(item)
                if copy_obj['src_path'] is not None and copy_obj['dst_path'] is not None:
                    copy_list.append(_parse_copy_data_from_obj(item))
    else:
        copy_obj = _parse_copy_data_from_obj([src, dest])
        copy_list.append(copy_obj)

    if threading is True:
        if len(copy_list) >= min_thread_threshold:
            _thread_file_action(copy_list, action="copy", max_threads=max_threads, min_thread_threshold=min_thread_threshold)
            return

    _copy_files_from_array(copy_list)
    # print(f"copy_list: {copy_list}")


def _copy_files_from_array(file_list):
    for file in file_list:
        os.makedirs(os.path.dirname(file['dst_path']), exist_ok=True)
        shutil.copy2(file['src_path'], file['dst_path'])
    return True


def _delete_single_file(file_path, shred=False):
    '''
        Deletes or shreds a single file.

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            Path to the file to delete.
        [`shred`=False] {bool}
            Securely shred the file (slower)

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


def _delete_files_from_array(file_list, shred=False):
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
        if exists(file):
            result = _delete_single_file(file, shred=shred)
            if result is not True:
                success = False
    return success


def _thread_file_action(file_list, **kwargs):
    max_threads = obj.get_kwarg(["max_threads"], 15, (int), **kwargs)
    min_thread_threshold = obj.get_kwarg(["min thread threshold", "min files thread"], 100, (int), **kwargs)
    action = obj.get_kwarg(["action"], "copy", (str), **kwargs)
    shred = obj.get_kwarg(["shred"], False, (bool), **kwargs)

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
            threads.append(Thread(target=_copy_files_from_array, args=(files_array,)))
        if action == "delete":
            threads.append(Thread(target=_delete_files_from_array, args=(files_array, shred)))

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

            `exclude`=[] {list}
                A list of keys to exclude from the returning dictionary.
                This is primarily useful for limiting the time/size of the operation.

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

    exclude = obj.get_kwarg(['exclude'], [], (list, str), **kwargs)
    file_path = strUtils.format.file_path(file_path)
    if exists(file_path):
        # print(f"file exists: {file_path}")
        # print(f"Getting data for file: {file_path}")
        try:
            file_data = {}
            file_data['file_name'] = os.path.basename(file_path)
            # ext = os.path.splitext(file_data['file_name'])
            file_data['extension'] = get_ext(file_path)
            file_data['name_no_ext'] = get_name_no_ext(file_path)
            file_data['file_path'] = file_path

            if 'dir_path' not in exclude:
                file_data['dir_path'] = os.path.dirname(file_path)
            if 'access_time' not in exclude:
                file_data['access_time'] = get_access_time(file_path)
            if 'modified_time' not in exclude:
                file_data['modified_time'] = get_modified_time(file_path)
            if 'created_time' not in exclude:
                file_data['created_time'] = get_create_time(file_path)
            if 'size' not in exclude:
                file_data['size'] = os.path.getsize(file_path)

            return file_data
        except FileNotFoundError as error:
            logger.warning(f"Error: {error}")
            return None
    else:
        logger.warning(f"Failed to find the file: {file_path}")


def get_modified_time(file_path):
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
    mod_time = os.path.getmtime(file_path)
    return int(datetime.fromtimestamp(mod_time).replace(tzinfo=timezone.utc).timestamp())


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


# file = r"C:\Users\Colemen\Desktop\DAZDOW~1\poses\STANDI~1\IM0008~1\Content\People\GENESI~2\Poses\AEONSO~1\STANDI~1\LIMBSL~1\SC-WE'~2.DUF"
# file = r"C:\\Users\\Colemen\\Desktop\\DAZ DOWNLOADS\\poses\\Standing Conversation Poses for Genesis 8\\IM00083571-01_StandingConversationPosesforGenesis8\\Content\\People\\Genesis 8 Male\\Poses\\Aeon Soul\\Standing Conversation\\Limbs Legs\\SC-We're all in the same boat Legs-M Genesis 8 Male.duf"
# clean = clean_path(file)
# print(f"clean file path: {clean}")
# print(exists(clean))
# file = strUtils.format.file_path(file)
# get_data(file)

# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=bare-except
# pylint: disable=line-too-long
'''
    Contains the general methods for manipulating directories.
'''

# import json
# from re import search
# import time
# import json
# from threading import Thread
import traceback
import shutil
import os
from pathlib import Path
import logging

import ftputil
from ftputil.error import FTPOSError
import colemen_string_utils as strUtils
import utils.file as file
import utils.objectUtils as obj
import utils.file_write as write
# import utils.file as f
import utils.resources


logger = logging.getLogger(__name__)


def get_files(search_path=False, **kwargs):
    return file.get_files(search_path, **kwargs)


def create(path, dir_name=False, **kwargs):
    '''
        Create a directory or path of directories on the local machine or an FTP server.

        ----------

        Arguments
        -------------------------
        `path` {str}
            The path to create or a path to where it should create the dir_name directory
        [`dir_name`=False] {str}
            The name of the directory to create.

        Keyword Arguments
        -----------------
        [`ftp`=None] {obj}
            A reference to the ftputil object.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:33:50
        `memberOf`: dir
        `version`: 1.0
        `method_name`: create
    '''
    success = False
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if dir_name is not False:
        path = os.path.join(path, dir_name)

    if ftp is not None:
        try:
            if ftp.path.exists(path) is False:
                ftp.makedirs(path, exist_ok=True)
                success = True
        except ftputil.error.PermanentError as error:
            print(f"error: {str(error)}")
            print(traceback.format_exc())
    else:
        if exists(path) is False:
            Path(path).mkdir(parents=True, exist_ok=True)
            if exists(path) is True:
                success = True
        else:
            success = True

    return success


def exists(file_path, **kwargs):
    '''
        Confirms that the directory file_path exists

        ----------

        Arguments
        -------------------------
        `file_path` {str}
            The path to confirm.

        Keyword Arguments
        -----------------
        [`ftp`=None] {obj}
            A reference to the ftputil object.

        Return {bool}
        ----------------------
        True if the directory exists, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:44:03
        `memberOf`: dir
        `version`: 1.0
        `method_name`: exists
    '''
    dir_exists = False
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)

    if ftp is not None:
        dir_exists = exists_ftp(file_path, ftp)
    else:
        if os.path.isdir(file_path) is True:
            dir_exists = True

    return dir_exists


def exists_ftp(file_path, ftp):
    '''
        Checks if an FTP directory exists.

        ----------

        Arguments
        -------------------------
        `file_path` {str}
            The path to confirm.

        `ftp` {obj}
            A reference to the ftputil object.

        Return {bool}
        ----------------------
        True if the directory exists, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:59:05
        `memberOf`: dir
        `version`: 1.0
        `method_name`: exists_ftp
    '''
    dir_exists = False
    try:
        if ftp.path.exists(file_path):
            dir_exists = True
    except ftputil.error.PermanentError as error:
        print(f"error: {str(error)}")
    return dir_exists


def get_folders(search_path=False, **kwargs):
    '''
        Get all directories from the search_path.

        ----------

        Arguments
        -------------------------
        `search_path` {str|list}
            The search path or list of paths to iterate.\n
            This is the same as the keyword argument search_path,
            the kwarg is provided for consistency.

        Keyword Arguments
        -----------------
            [`search_path`=cwd] {str|list}
                The search path or list of paths to iterate.

            [`recursive`=True] {boolean}
                If True the path is iterated recursively

            [`exclude`=[]] {str|list}
                A string or list of strings, if the file path contains any of them,
                the directory is ignored.

            [`include`=[]] {str|list}
                A string or list of strings, if the file path does NOT contain any of them,
                the directory is ignored.

            [`paths_only`=False] {bool}
                If True, the returned value will be a list of directory paths.

            [`ftp`=None] {obj}
                A reference to the ftputil object.

        Return {list}
        ----------------------
        A list of dictionaries containing all matching directories.\n
        example:\n
            [{\n
                file_path:"beep/boop/bleep/blorp",\n
                dir_name:"blorp"\n
            },...]\n
        if paths_only = True:\n
            ["beep/boop/bleep/blorp",...]

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 12:17:24
        `memberOf`: dir
        `version`: 1.0
        `method_name`: get_folders
    '''
    dir_array = []
    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (list, str), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]

    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    paths_only = obj.get_kwarg(['paths only', 'path only'], False, (bool), **kwargs)

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is not None:
        return get_folders_ftp(search_path, **kwargs)

    for path in search_path:
        # # pylint: disable=unused-variable
        for root, folders, files in os.walk(path):
            # print(folders)
            for current_dir in folders:
                if paths_only:
                    dir_array.append(os.path.join(root, current_dir))
                    continue
                dir_data = {}
                dir_data['dir_name'] = current_dir
                dir_data['file_path'] = os.path.join(root, current_dir)
                ignore = False
                if len(exclude) > 0:
                    if strUtils.parse.array_in_string(exclude, dir_data['file_path']) is True:
                        continue
                if len(include) > 0:
                    if strUtils.parse.array_in_string(include, dir_data['file_path']) is False:
                        continue
                # if ignore_array is not False:
                #     for x in ignore_array:
                #         if x in dir_data['file_path']:
                #             ignore = True

                # if ignore is False:

                dir_array.append(dir_data)

            if recursive is False:
                break
    return dir_array


def get_folders_ftp(search_path=False, **kwargs):
    '''
        Get all directories from the search_path.

        ----------

        Arguments
        -------------------------
        `search_path` {str|list}
            The search path or list of paths to iterate.\n
            This is the same as the keyword argument search_path,
            the kwarg is provided for consistency.

        Keyword Arguments
        -----------------
            [`search_path`=cwd] {str|list}
                The search path or list of paths to iterate.

            `ftp` {obj}
                A reference to the ftputil object.

            [`recursive`=True] {boolean}
                If True the path is iterated recursively

            [`exclude`=[]] {str|list}
                A string or list of strings, if the file path contains any of them,
                the directory is ignored.

            [`include`=[]] {str|list}
                A string or list of strings, if the file path does NOT contain any of them,
                the directory is ignored.

            [`paths_only`=False] {bool}
                If True, the returned value will be a list of directory paths.


        Return {list}
        ----------------------
        A list of dictionaries containing all matching directories.\n
        example:\n
            [{\n
                file_path:"beep/boop/bleep/blorp",\n
                dir_name:"blorp"\n
            },...]\n
        if paths_only = True:\n
            ["beep/boop/bleep/blorp",...]

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 12:31:27
        `memberOf`: dir
        `version`: 1.0
        `method_name`: get_folders_ftp
    '''
    dir_array = []
    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (list, str), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]

    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    paths_only = obj.get_kwarg(['paths only', 'path only'], False, (bool), **kwargs)

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is None:
        logger.warning("No FTP obj reference provided.")
        return False

    # print(f"search_path: {search_path}")
    for path in search_path:
        # # pylint: disable=unused-variable
        for root, folders, files in ftp.walk(path):
            # print(folders)
            for current_dir in folders:
                if paths_only:
                    dir_array.append(os.path.join(root, current_dir))
                    continue
                dir_data = {}
                dir_data['dir_name'] = current_dir
                dir_data['file_path'] = os.path.join(root, current_dir)
                ignore = False
                if len(exclude) > 0:
                    if strUtils.parse.array_in_string(exclude, dir_data['file_path']) is True:
                        continue
                if len(include) > 0:
                    if strUtils.parse.array_in_string(include, dir_data['file_path']) is False:
                        continue

                dir_array.append(dir_data)

            if recursive is False:
                break
    return dir_array


def index_files(start_path, extension_array=None, ignore_array=None, recursive=True):
    '''
        Iterates the start_path to find all files within.

        ----------
        Arguments
        -----------------

            `search_path`=cwd {str|list}
                The search path or list of paths to iterate.
            `ignore`=[] {str|list}
                A term or list or terms to ignore if the file path contains any of them.
            `extensions`=[] {str|list}
                An extension or list of extensions that the file must have.
            `recursive`=True {boolean}
                If True the path is iterated recursively

        return
        ----------
        `return` {str}
            A list of dictionaries containing all matching files.
    '''
    if isinstance(extension_array, list) is False:
        extension_array = []
    if isinstance(ignore_array, list) is False:
        ignore_array = []
    file_array = []
    # pylint: disable=unused-variable
    for root, folders, files in os.walk(start_path):
        for file in files:
            file_data = file.get_data(os.path.join(root, file))
            ignore = False

            if len(extension_array) > 0:
                if file_data['extension'] not in extension_array:
                    ignore = True

            if len(ignore_array) > 0:
                for ignore_string in ignore_array:
                    if ignore_string in file_data['file_path']:
                        ignore = True

            if ignore is False:
                # fd['file_hash'] = generateFileHash(fd['file_path'])
                file_array.append(file_data)

        if recursive is False:
            break
    return file_array


def delete(file_path, ftp=None):
    '''
        Deletes a directory from the local machine or FTP server.

        ----------

        Arguments
        -------------------------
        `file_path` {str}
            The path of the directory to delete.

        [`ftp`=None] {obj}
            A reference to the ftputil object.


        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 11:56:21
        `memberOf`: dir
        `version`: 1.0
        `method_name`: delete
    '''
    success = False
    if ftp is not None:
        success = delete_ftp(file_path, ftp)
    else:
        try:
            shutil.rmtree(file_path)
            success = True
        except OSError as error:
            logger.warning("Failed to delete local directory: %s", file_path)
            logger.warning("Error: %s : %s", file_path, error.strerror)
            success = False
            # print("Error: %s : %s" % (file_path, error.strerror))
    return success


def delete_ftp(file_path, ftp):
    '''
        Deletes a directory on an FTP server.

        ----------

        Arguments
        -------------------------
        `file_path` {str}
            The path of the directory to delete.

        [`ftp`=None] {obj}
            A reference to the ftputil object.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 12:11:53
        `memberOf`: dir
        `version`: 1.0
        `method_name`: delete_ftp
    '''
    success = False
    if exists_ftp(file_path, ftp):
        # print(f"{file_path} exists.")
        try:
            ftp.rmtree(file_path)
            success = True
        except FTPOSError as error:
            logger.warning("Failed to delete FTP directory: %s", file_path)
            logger.warning("Error: %s : %s", file_path, error.strerror)
    else:
        success = True
    return success


def copy(src, dst=False, **kwargs):
    '''
        Copy a directory to another location.

        ----------

        Arguments
        -------------------------
        `src` {str|list|dict}
            The source directory to copy.\n
            A list of dictionaries/lists:\n
                [["xxx","aaa"],{src_path:"xxx",dst_path:"aaa"}]
            A dictionary:\n
                {src_path:"xxx",dst_path:"aaa"}

        Keyword Arguments
        -------------------------
        `ftp` {obj}
            A reference to the ftputil object.
        [`ftp_direction`='local_to_server'] {str}
            The direction of the copying:
                local_to_server: Copy local directories/files to the FTP server.
                server_to_local: Copy FTP server directories/files to the Local machine.

        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-19-2021 12:34:48
        `memberOf`: dir
        `version`: 1.0
        `method_name`: copy
    '''
    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    ftp_direction = obj.get_kwarg(["ftp direction"], 'local_to_server', (str), **kwargs)
    copy_list = [src, dst]
    if dst is False:
        copy_list = _parse_copy_data_from_obj(src)

    for dir_data in copy_list:
        if ftp is not None:
            if ftp_direction == 'local_to_server':
                mirror_to_server(dir_data['src_path'], dir_data['dst_path'], **kwargs)
        else:
            mirror(dir_data['src_path'], dir_data['dst_path'], **kwargs)


def mirror(src, dst, **kwargs):
    '''
        Mirrors a source directory to the destination directory.\n
        Optionally, copying files.\n

        ----------

        Arguments
        -------------------------
        `src` {str}
            The file path to be copied to the dst
        `dst` {str}
            The path to copy the src to.

        Keyword Arguments
        -------------------------
        [`empty_files`=False] {bool}
            If True, files are copied but have no contents.
        [`dirs_only`=False] {bool}
            If True, only directories are copied.
        [`recursive`=True] {bool}
            If True the path is iterated recursively
        [`exclude`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply to both files and directories.
        [`include`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply to both files and directories.
        [`exclude_dirs`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply only to directories.
        [`include_dirs`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply only to directories.
        [`exclude_files`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply only to files.
        [`include_files`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply only to files.
        [`ftp`=None] {obj}
            A reference to the ftputil object.
        [`ftp_direction`='local_to_server'] {str}
            The direction of the copying:
                local_to_server: Copy local directories/files to the FTP server.
                server_to_local: Copy FTP server directories/files to the Local machine.


        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-11-2021 14:34:12
        `memberOf`: dir
        `version`: 1.0
        `method_name`: mirror
    '''
    # if EMPTY_FILES is True, it creates a duplicate file with no content.
    empty_files = obj.get_kwarg(['empty files'], False, bool, **kwargs)
    dirs_only = obj.get_kwarg(['dirs only'], False, bool, **kwargs)
    recursive = obj.get_kwarg(['recursive', 'recurse'], True, (bool), **kwargs)
    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    exclude = obj.get_kwarg(['exclude'], [], (list, str), **kwargs)

    include_dirs = obj.get_kwarg(['include dirs'], include, (list, str), **kwargs)
    exclude_dirs = obj.get_kwarg(['exclude dirs'], exclude, (list, str), **kwargs)

    include_files = obj.get_kwarg(['include files'], include, (list, str), **kwargs)
    exclude_files = obj.get_kwarg(['exclude files'], exclude, (list, str), **kwargs)

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    ftp_direction = obj.get_kwarg(["ftp direction"], 'local_to_server', (str), **kwargs)

    if ftp is not None:
        if ftp_direction == "local_to_server":
            return mirror_to_server(src, dst, **kwargs)

    src = os.path.abspath(src)
    if exists(src) is False:
        logger.warning("Source path must exist.\nsource: %s", src)
        return False

    if exists(dst) is False:
        os.makedirs(dst)
    dirs = get_folders(search_path=src, recursive=recursive,
                       include=include_dirs, exclude=exclude_dirs)

    for folder in dirs:
        folder['dst_path'] = folder['file_path'].replace(src, dst)
        try:
            os.makedirs(folder['dst_path'], exist_ok=True)
            if dirs_only is False:
                files = file.get_files(search_path=folder['file_path'], include=include_files,
                                       exclude=exclude_files, recursive=False)
                # newlist = [x['dst_path'] = x['file_path'].replace(src, dst) for x in files]
                for file in files:
                    file['src_path'] = file['file_path']
                    file['dst_path'] = file['file_path'].replace(src, dst)
                # folder['dst_path'] = folder['file_path'].replace(src, dst)
                if empty_files is True:
                    for file in files:
                        write.write(file['dst_path'], "EMPTY TEST FILE CONTENT")
                else:
                    file.copy(files)
        except:
            # print(f"{traceback.format_exc()}")
            logger.warning("failed to create directory: %s", folder["dst_path"])
            logger.warning(traceback.format_exc())


def mirror_to_server(src, dst, **kwargs):
    '''
        Mirrors the local source directory to the FTP destination directory.
        Optionally, copying files.

        ----------

        Arguments
        -------------------------
        `src` {str}
            The LOCAL file path to be copied to the dst
        `dst` {str}
            The FTP path to copy the src to.

        Keyword Arguments
        -------------------------
        `ftp` {obj}
            A reference to the ftputil object.
        [`dirs_only`=False] {bool}
            If True, only directories are copied.
        [`recursive`=True] {bool}
            If True the path is iterated recursively
        [`exclude`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply to both files and directories.
        [`include`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply to both files and directories.
        [`exclude_dirs`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply only to directories.
        [`include_dirs`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply only to directories.
        [`exclude_files`=[]] {str|list}
            A string or list of strings, if the file path contains any of them,
            the directory is ignored.\n
            If provided, these rules apply only to files.
        [`include_files`=[]] {str|list}
            A string or list of strings, if the file path does NOT contain any of them,
            the directory is ignored.\n
            If provided, these rules apply only to files.



        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-11-2021 14:34:12
        `memberOf`: dir
        `version`: 1.0
        `method_name`: mirror
    '''
    # if EMPTY_FILES is True, it creates a duplicate file with no content.
    dirs_only = obj.get_kwarg(['dirs only'], False, bool, **kwargs)
    recursive = obj.get_kwarg(['recursive', 'recurse'], True, (bool), **kwargs)
    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    exclude = obj.get_kwarg(['exclude'], [], (list, str), **kwargs)

    include_dirs = obj.get_kwarg(['include dirs'], include, (list, str), **kwargs)
    exclude_dirs = obj.get_kwarg(['exclude dirs'], exclude, (list, str), **kwargs)

    include_files = obj.get_kwarg(['include files'], include, (list, str), **kwargs)
    exclude_files = obj.get_kwarg(['exclude files'], exclude, (list, str), **kwargs)

    ftp = obj.get_kwarg(["ftp"], None, None, **kwargs)
    if ftp is None:
        logger.warning("No FTP object provided.")
        return False

    src = os.path.abspath(src)
    if exists(src) is False:
        logger.warning("Source path must exist.\nsource: %s", src)
        return False

    if exists(dst, ftp=ftp) is False:
        create(dst, ftp=ftp)

    dirs = get_folders(search_path=src, recursive=recursive,
                       include=include_dirs, exclude=exclude_dirs, ftp=ftp)

    for folder in dirs:
        folder['dst_path'] = folder['file_path'].replace(src, dst)
        try:
            create(folder['dst_path'], ftp=ftp)
            if dirs_only is False:
                files = file.get_files(search_path=folder['file_path'], include=include_files,
                                       exclude=exclude_files, recursive=False, ftp=ftp)
                # newlist = [x['dst_path'] = x['file_path'].replace(src, dst) for x in files]
                for file in files:
                    file['src_path'] = file['file_path']
                    file['dst_path'] = file['file_path'].replace(src, dst)
                file.copy(files, ftp=ftp)
        except:
            logger.warning("failed to create directory: %s", folder["dst_path"])
            logger.warning(traceback.format_exc())


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


# file = r"C:\Users\Colemen\Desktop\DAZ DOWNLOADS\poses"
# get_files(file)
# src = r"C:\Users\Colemen\Desktop\TEST_FOLDER\directoryMirrorTests\sourceDirectory"
# dst = r"C:\Users\Colemen\Desktop\TEST_FOLDER\directoryMirrorTests\targetDirectory"
# mirror(src, dst)

# src = r"Z:\Structure\Ra9\2021"
# start_time = time.time()
# get_files_thread(src)
# end_time = time.time()
# print(f"indexing duration: {end_time - start_time}")

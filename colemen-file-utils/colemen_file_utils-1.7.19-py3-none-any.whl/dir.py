'''
    Contains the general methods for manipulating directories.
'''
# import json
import json
import traceback
import shutil
import os
from pathlib import Path
import objectUtils as obj
import file_write as write
import string_utils as strUtils
import file as f
import logging

logger = logging.getLogger(__name__)

# todo - DOCUMENTATION FOR METHODS


def create(path, dir_name=False):
    if dir_name is not False:
        path = os.path.join(path, dir_name)

    if exists(path) is False:
        Path(path).mkdir(parents=True, exist_ok=True)
        # os.mkdir(path)
        if exists(path) is True:
            return True
    else:
        return True


def exists(file_path):
    if os.path.isdir(file_path) is True:
        return True
    else:
        return False


def get_folders(search_path=False, **kwargs):
    dir_array = []
    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), str, **kwargs)
    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)
    # ignore_array = obj.get_kwarg(['ignore', 'ignore_array'], [], list, **kwargs)

    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    # print(f"search_path: {search_path}")

    # # pylint: disable=unused-variable
    for root, folders, files in os.walk(search_path):
        # print(folders)
        for current_dir in folders:
            dir_data = {}
            dir_data['dir_name'] = current_dir
            dir_data['file_path'] = os.path.join(root, current_dir)
            ignore = False
            if len(exclude) > 0:
                if array_in_string(exclude, dir_data['file_path']) is True:
                    continue
            if len(include) > 0:
                if array_in_string(include, dir_data['file_path']) is False:
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


def get_files(search_path=False, **kwargs):
    '''
        Get all files/data from the search_path.

        ----------
        Keyword Arguments
        -----------------

            `search_path`=cwd {str|list}
                The search path or list of paths to iterate.
            `recursive`=True {boolean}
                If True the path is iterated recursively
            `ignore`=[] {str|list}
                A term or list or terms to ignore if the file path contains any of them.
            `extensions`=[] {str|list}
                An extension or list of extensions that the file must have.

        return
        ----------
        `return` {str}
            A list of dictionaries containing all matching files.
    '''
    file_array = []
    if search_path is False:
        search_path = obj.get_kwarg(['search path', 'search'], os.getcwd(), (str, list), **kwargs)
    if isinstance(search_path, list) is False:
        search_path = [search_path]

    recursive = obj.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)

    # ignore_array = obj.get_kwarg(['ignore', 'ignore_array', 'exclude'], [], (str, list), **kwargs)
    exclude = obj.get_kwarg(['exclude', 'ignore', 'ignore array'], [], (list, str), **kwargs)
    if isinstance(exclude, (str)):
        exclude = [exclude]

    include = obj.get_kwarg(['include'], [], (list, str), **kwargs)
    if isinstance(include, (str)):
        include = [include]

    extension_array = strUtils.format_extension(obj.get_kwarg(['extensions', 'ext', 'extension'], [], (str, list), **kwargs))
    if isinstance(extension_array, (str)):
        extension_array = [extension_array]

    # print(json.dumps(extension_array, indent=4))
    for path in search_path:
        # pylint: disable=unused-variable
        for root, folders, files in os.walk(path):
            for file in files:
                file_data = f.get_data(os.path.join(root, file))
                if file_data is not None:
                    # ignore = False
                    # print(f"file_data['extension']: {file_data['extension']}")
                    if len(exclude) > 0:
                        if array_in_string(exclude, file_data['file_path']) is True:
                            continue

                    if len(include) > 0:
                        if array_in_string(include, file_data['file_path']) is False:
                            continue

                    if len(extension_array) > 0:
                        file_ext = strUtils.format_extension(file_data['extension'])
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
            file_data = f.get_data(os.path.join(root, file))
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


def delete(filePath):
    try:
        shutil.rmtree(filePath)
    except OSError as e:
        print("Error: %s : %s" % (filePath, e.strerror))


def array_in_string(array, value, default=False):
    if len(array) == 0:
        return default
    if isinstance(value, (str)) is False:
        logger.warning('Second argument of array_in_string, must be a string.')
        logger.warning(value)
        return default
    for item in array:
        if item in value:
            return True
    return default


def copy(src, dst=False):
    copy_list = [src, dst]
    if dst is False:
        copy_list = f._parse_copy_data_from_obj(src)
    for dir in copy_list:
        mirror(dir['src_path'], dir['dst_path'])


def mirror(src, dst, **kwargs):
    '''
        Mirrors a source directory to the destination directory.
        Optionally, copying files.

        ----------

        Arguments
        -------------------------
        `arg_name` {type}
                arg_description

        Keyword Arguments
        -------------------------
        `arg_name` {type}
                arg_description

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

    src = os.path.abspath(src)
    if exists(src) is False:
        logger.warning(f"Source path must exist.\nsource: {src}")

    if exists(dst) is False:
        os.makedirs(dst)
    dirs = get_folders(search_path=src, recursive=recursive, include=include_dirs, exclude=exclude_dirs)

    for folder in dirs:
        folder['dst_path'] = folder['file_path'].replace(src, dst)
        try:
            os.makedirs(folder['dst_path'], exist_ok=True)
            if dirs_only is False:
                files = get_files(search_path=folder['file_path'], include=include_files, exclude=exclude_files, recursive=False)
                # newlist = [x['dst_path'] = x['file_path'].replace(src, dst) for x in files]
                for file in files:
                    file['src_path'] = file['file_path']
                    file['dst_path'] = file['file_path'].replace(src, dst)
                # folder['dst_path'] = folder['file_path'].replace(src, dst)
                if empty_files is True:
                    for file in files:
                        write.write(file['dst_path'], "EMPTY TEST FILE CONTENT")
                else:
                    f.copy(files)
        except:
            # print(f"{traceback.format_exc()}")
            logger.warning(f'failed to create directory: {folder["dst_path"]}')
            logger.warning(traceback.format_exc())


file = r"C:\Users\Colemen\Desktop\DAZ DOWNLOADS\poses"
get_files(file)
# src = r"C:\Users\Colemen\Desktop\TEST_FOLDER\directoryMirrorTests\sourceDirectory"
# dst = r"C:\Users\Colemen\Desktop\TEST_FOLDER\directoryMirrorTests\targetDirectory"
# mirror(src, dst)

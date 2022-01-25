import json
# import shutil
import os
import re
# from pathlib import Path
import objectUtils as objUtils
import file_read as read
import string_utils as strUtils

# todo - DOCUMENTATION FOR METHODS


def by_name(file_name, search_path=None, **kwargs):
    '''
        Searches the path provided for files that match the file_name

        ----------
        Arguments
        -----------------
        `file_name` {str|list}
            The string or list of strings to search for.
        `search_path`=cwd {str}
            The directory to search within.

        Keyword Arguments
        -----------------
            `recursive`=True {boolean}
                If True the path is searched recursively

            `case_sensitive`=True {bool}
                If False case is ignored.
            `exact_match`=True {bool}
                If False it will match with any file that contains the file_name argument
            `regex`=False {bool}
                If True the file_name arg is treated as a regex string for comparisons.

        Return
        ----------
        `return` {None|list}
            A list of matching files or None if no matching files are found.
    '''
    if isinstance(file_name, list) is False:
        file_name = [file_name]
    if search_path is None:
        search_path = os.getcwd()

    extensions = strUtils.format_extension(objUtils.get_kwarg(['extensions', 'ext'], [], (list, str), **kwargs))
    if isinstance(extensions, str):
        extensions = [extensions]

    recursive = objUtils.get_kwarg(['recursive', 'recurse'], True, bool, **kwargs)
    case_sensitive = objUtils.get_kwarg(['case_sensitive'], True, (bool), **kwargs)
    exact_match = objUtils.get_kwarg(['exact_match'], True, (bool), **kwargs)
    regex = objUtils.get_kwarg(['regex', 'use regex'], False, (bool), **kwargs)

    if case_sensitive is False and regex is False:
        new_name_array = []
        for name in file_name:
            if isinstance(name, str):
                new_name_array.append(name.lower())
        file_name = new_name_array

    result_array = []
    # pylint: disable=unused-variable
    # pylint: disable=too-many-nested-blocks
    for root, folders, files in os.walk(search_path):
        for file in files:
            skip = False
            current_file_path = os.path.join(root, file)
            test_file_name = file

            test_file_ext = strUtils.format_extension(os.path.splitext(os.path.basename(current_file_path))[1])
            if case_sensitive is False:
                test_file_name = test_file_name.lower()

            if len(extensions) > 0:
                if test_file_ext not in extensions:
                    skip = True

            if skip is False:
                for name in file_name:
                    if len(name) == 0 or "*" == name:
                        result_array.append(current_file_path)
                        break

                    if regex is not False:
                        match = re.search(name, test_file_name)
                        if match is not None:
                            result_array.append(current_file_path)

                    if exact_match is True:
                        if test_file_name == name:
                            result_array.append(current_file_path)
                    else:
                        if name in test_file_name:
                            result_array.append(current_file_path)
        if recursive is False:
            break

    if len(result_array) > 0:
        return result_array
    return None

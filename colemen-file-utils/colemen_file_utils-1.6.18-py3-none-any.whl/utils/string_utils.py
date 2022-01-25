"""
    String manipulation/generation utilities used by other modules.
"""

import json
import shutil
import re
from pathlib import Path
import hashlib
import utils.objectUtils as objUtils
import utils.file_read as read


# todo - DOCUMENTATION FOR METHODS

# def parse_size(string):
#     known_sizes = ['b']


def sanitize_windows_file_name(file_name):
    '''
        Strips (window's) invalid characters from the file_name.

        ----------
        `file_name` {str}
            The string to be parsed.

        ----------
        `return` {str}
            The parsed string
    '''
    return re.sub(r'[<>:"/\|?*]*', "", file_name)


def generate_hash(value):
    """
        Generates a sha256 hash from the string provided.

        ----------
        `value` {str}
            The string to calculate the hash on.

        ----------
        `return` {str}
            The sha256 hash
    """
    jsonStr = json.dumps(value).encode('utf-8')
    hex_dig = hashlib.sha256(jsonStr).hexdigest()
    return hex_dig


def format_extension(string):
    """
        Formats a file extension to have no leading period.

        ----------
        `value` {str|list}
            The file extension or list of extensions to format

        ----------
        `return` {str}
            The formatted file extension
    """
    new_ext_array = []
    if isinstance(string, list) is False:
        string = [string]

    for ext in string:
        # print(f"ext: {ext}")
        ext = ext.lower()
        ext = re.sub(r"^\.*", '', ext)
        new_ext_array.append(ext)

    if len(new_ext_array) == 1:
        return new_ext_array[0]
    return new_ext_array


def dynamic_regex_search(string, regex):
    """
        Formats a file extension to have no leading period.

        ----------
        `value` {str|list}
            The file extension or list of extensions to format

        ----------
        `return` {str}
            The formatted file extension
    """
    match = re.search(regex, string)
    if match is not None:
        return match
    return False

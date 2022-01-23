import json
# import shutil
import os
import re
# from pathlib import Path
import utils.objectUtils as objUtils
import utils.file_read as read

# todo - DOCUMENTATION FOR METHODS


def write(file_path, contents=None, **kwargs):
    '''
        Writes the contents to the file_path.
        @function write
    '''
    to_json = objUtils.get_kwarg(['json', 'to json'], False, bool, **kwargs)
    size = objUtils.get_kwarg(['size', 'file_size'], None, int, **kwargs)
    append = objUtils.get_kwarg(['append'], False, bool, **kwargs)

    if size is not None:
        of_size(file_path, size)
        return

    if to_json is not False:
        to_json(file_path, contents)
        return

    if append is True:
        append(file_path, contents)
        return

    f = open(file_path, "w")
    f.write(contents)
    f.close()


def append(file_path, contents):
    '''
        appends the contents to the file_path.
        if the content provided is not a string, it is converted to JSON.
    '''
    if isinstance(contents, str) is False:
        contents = json.dumps(contents, indent=4)
    f = open(file_path, "a")
    f.write(contents)
    f.close()


def of_size(file_path, kb_size):
    '''
        Write a file that is of a specific size.
        @param {string} file_path - The path to the file to write.
        @param {int} kb_size - The size of the file to write in kilobytes
    '''
    # kb_size = size
    # kb_size = size * (1024 * 1024)
    with open(file_path, "wb") as out:
        out.truncate(kb_size)


def to_json(file_path, content, indent=4):
    '''
        Write or append to a json file.
        @function to_json

        @param {string} file_path - The path to the file to write.
        @param {mixed} content - The content to be written to the json file
        @param {int} [indent=4] - The pretty print indent setting for the JSON output.
    '''

    json_str = json.dumps(content, indent=indent)
    f = open(file_path, "w")
    f.write(json_str)
    f.close()

""" Example io_functions

This module provides different io functions

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

"""

import glob
import os
import sys


def read_file(filename):
    """Read file

    Nothing special

    Args:
      filename (str): File to read

    Returns:
      str: content of file
    """
    with open(filename, "r") as file_object:
        # Append 'hello' at the end of file
        content = file_object.read()
    return content


def write_file(filename, content):
    """Write file

    Args:
      filename (string): File to write
      content (string): content which will be written to file

    Returns:
      None: nothing
    """
    with open(filename, "w") as file_object:
        file_object.write(content)


def get_all_files_from_folder(folder, extension=""):
    """ Get all files from a folder

    Args:
      folder (string): folder
      extension (string): extension e.g. .md

    Returns:
      List[str]: filename of files in folder
    """
    list_of_files_full = glob.glob(str(folder + "/*" + extension))
    list_of_files = []
    for filename_full in list_of_files_full:
        filename = os.path.basename(filename_full)
        list_of_files.append(filename)
    return list_of_files


def get_all_folders_from_folder(start_folder):
    """ Get all folders from a folder

    Args:
      start_folder (string): folder

    Returns:
      List[str]: name of folders in folder

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
    try:
        folders = next(os.walk(start_folder))[1]
        print(folders)
    except StopIteration:
        folders = []
        print(f"folder {start_folder} not found")
    except:  # noqa
        folders = []
        print("Unexpected error:", sys.exc_info())

    return folders

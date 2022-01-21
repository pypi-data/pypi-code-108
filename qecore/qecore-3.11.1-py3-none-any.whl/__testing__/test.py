#!/usr/bin/env python3

import os


def file_loader(self, file_name="tmp"):
    """
    Load content from file or upon UnicodeDecodeError debug the location of the error and return replaced data.

    :type file_name: str
    :param file_name: String representation of file location.

    :return: File data or some debug data and file content replaced in places that were not readable.
    :rtype: str
    """

    _file_data = ""
    if not os.path.isfile(file_name):

        return "File does not exist."

    try:
        _file_data = open(file_name, "r").read()

    except UnicodeDecodeError as error:

        # Gather all lines that contain non-ASCII characters.
        _file = open(file_name, "rb")
        non_ascii_lines = [line for line in _file if any(_byte > 127 for _byte in line)]
        _file.close()

        # Attempt to load the file and replace all error data.
        file_content = open(file_name, "r", encoding="utf-8", errors="replace").read()

        _file_data = f"\nException detected:\n{error}"
        _file_data += f"\nDetected non-ASCII lines:\n{non_ascii_lines}" if any(non_ascii_lines) else "None"
        _file_data += f"\nReplaced file content:\n{file_content}"


    return _file_data


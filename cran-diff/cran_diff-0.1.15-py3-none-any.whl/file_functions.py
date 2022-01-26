"""
Functions / utilities for working with files and filepaths
"""

import pathlib


def read_file(filepath: pathlib.Path) -> str:
    """
    Reads a file that may or may not be UTF8-encoded.
    When the file is not UTF-8 encoded, it is converted to UTF-8 before reading

    :param   filepath: The path to a file that is to be read in
    :type   filepath: pathlib.Path

    :return: string of data, as read from the file
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file_handle:
            data = file_handle.read()
    except UnicodeDecodeError:
        # Need to convert to UTF-8
        converted_file = convert_to_utf8(filepath)
        with open(converted_file, "r", encoding="utf-8") as file_handle:
            data = file_handle.read()
    return data


def convert_to_utf8(filename: pathlib.Path) -> pathlib.Path:
    """Use UTF-8 encoding in file

    :param: filename: file to decode using latin1
    :return: name of new file that uses UTF-8 encoding
    """
    BLOCKSIZE = 1024 * 1024
    converted_file = pathlib.Path(str(filename) + "_utf-8")
    with open(filename, "rb") as inf:
        with open(converted_file, "wb") as ouf:
            while True:
                data = inf.read(BLOCKSIZE)
                if not data:
                    break
                converted = data.decode("latin1").encode("utf-8")
                ouf.write(converted)
    return converted_file

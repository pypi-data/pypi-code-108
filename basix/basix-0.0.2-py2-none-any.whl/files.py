#!/usr/bin/python
import os
import logging
import sys
import shutil
from pathlib import Path


def read_file(file: str) -> str:
    """Read a file content

    :param file: path to the file
    :type file: str
    :return: A string with the file content
    :rtype: str
    """
    with open(file, "r") as file:
        private_key = file.read()
    return private_key


def file_print(
    content, file: str, mode: str = "write", sep: str = " ", end: str = "\n", **kwargs
) -> None:
    """Print the content to file

    :param content: Content to be printed
    :type content:
    :param file: path to the file
    :type file: str
    :param mode: write mode. Can be 'write' or 'append', defaults to "write"
    :type mode: str, optional
    :param sep: string inserted between values, defaults to " "
    :type sep: str, optional
    :param end: string appended after the last value, defaults to "\n"
    :type end: str, optional
    """
    if mode == "write":
        mode = "w"
    elif mode == "append":
        mode = "a"

    with open(file, mode) as text_file:
        print(content, file=text_file, sep=sep, end=end, **kwargs)


def make_directory(path, parents=True, exist_ok=True):
    """Creates a dict if it does not exists.

    :param path: path of new directory
    :type path: str
    """

    try:
        if parents:
            Path(path).mkdir(parents=parents, exist_ok=exist_ok)

        else:
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                logging.error(f"Directory '{path}' not found")

    except Exception as err:
        logging.error(err)


def remove_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)

        except Exception as err:
            logging.error(err)
    else:
        logging.error(f"File '{file_path}' not found")


def remove_empty_directory(folder_path):
    if os.path.exists(folder_path):
        if len(os.listdir(folder_path)) == 0:
            try:
                os.rmdir(folder_path)

            except Exception as err:
                logging.error(err)
        else:
            logging.error(f"Folder '{folder_path}' is not empty")
    else:
        logging.error(f"Directory '{folder_path}' not found")


def remove_directory_recursively(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except Exception as err:
            logging.error(err)
    else:
        logging.error(f"Directory '{folder_path}' not found")


def remove_directory(folder_path, recursive=False):
    if recursive:
        remove_directory_recursively(folder_path)
    else:
        remove_empty_directory(folder_path)

"""
description: this module provides the class Directory.
"""

import os


class Directory:
    """
    description: this class is used to change directory temporary.
    """
    __directory = None
    __current_directory = None

    def __init__(self, directory):
        self.__directory = directory
        self.__current_directory = os.path.abspath(os.curdir)

    def __enter__(self):
        os.chdir(self.__directory)

    def __exit__(self, *args, **kwargs):
        os.chdir(self.__current_directory)

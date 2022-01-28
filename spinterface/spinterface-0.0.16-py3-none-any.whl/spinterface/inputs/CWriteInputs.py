# -*- coding: utf-8 -*-
r"""
This module takes care of writing input files for calculations with the spindynamic program. To achieve forward
compatability you can define all the key value pairs while initializing this class
"""
import shutil
from typing import TypeVar, List
from pathlib import Path
import fileinput
import os


class CWriteInput:
    r"""
    General class for writing input files
    """

    def __init__(self, name: str, lines: List[str] = [], **kwargs) -> None:
        r"""
        Initializes writing of input file. The key value pairs of the arguments are passed towards the input file.
        To create the file you need to call this class

        Args:
            name(str): name of the created file
            lines: a list of lines which shall be added to the input file. This can be used if there are lines without
            a specific key
        """
        self.file = name
        if os.path.isfile(self.file):
            print(f'file {name} already exists. Will replace it.')
            os.remove(self.file)
        self.content = dict(**kwargs)
        self.contentlines = lines

    def __call__(self, where: Path = Path.cwd()) -> None:
        r"""
        Calls the writing

        Args:
            where(Path): In which directory shall the file be created with the name given in the initializer
        """
        self.where = where
        with open(str(where / self.file), 'a') as f:
            for (key, value) in self.content.items():
                f.write(key + ' ' + value + '\n')
            for line in self.contentlines:
                f.write(line + '\n')

    def appendline(self, value: str) -> None:
        r"""
        Appends a line to the input file
        """
        self.contentlines.append(value)

    def adjustparameter(self, key: str, value: str) -> None:
        r"""
        Adjust the parameter in the object. You have to call this object again to write.

        Args:
            key: str
            value: str
        """
        try:
            self.content[key] = value
        except KeyError:
            print(f'Key ({key}) not found in {self.file}. Will ignore command.')

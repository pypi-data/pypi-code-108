import os
from os.path import dirname, isfile, join
from sys import path


def insert_path_by_identified_file(identified_file: str):
    root = os.getcwd()

    while root and not isfile(join(root, identified_file)):
        root = dirname(root)
        print(root)

    if not root:
        raise IOError(f'Cannot found ${identified_file}')

    path.insert(0, root)

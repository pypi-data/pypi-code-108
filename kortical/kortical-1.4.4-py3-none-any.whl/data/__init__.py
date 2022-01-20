import os
import inspect

module_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def get_names():
    with open(f'{module_directory}/names.txt') as f:
        names = set([n[:-1] for n in f.readlines()])
        return names

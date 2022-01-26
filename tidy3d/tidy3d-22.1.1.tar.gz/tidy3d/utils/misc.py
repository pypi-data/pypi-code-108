import numpy as np
import subprocess
import logging
from ..constants import inf
from .log import log_and_raise


def listify(obj):
    # Make a list if not a list
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return [obj]


def list2str(li, elem_format):
    # Make a string that looks like the list ``li`` using %-specifying string 
    # ``elem_format`` for each element

    def ef(element):
        if element==inf:
            return "inf"
        else:
            return elem_format % element

    return "[" + ", ".join([ef(elem) for elem in li]) + "]"


def eps_input(value, name):
    """Convert 'value' to a size-3 array to be used as anisotropic permittivity/conductivity,
    or raise an error if not possible.
    """
    if isinstance(value, int) or isinstance(value, float):
        value = value * np.ones((3,))
    try:
        value = np.array(value)
        if value.size==1:
            value = np.tile(value, (3,))
        assert value.size == 3
    except:
        log_and_raise(f"Wrong '{name}' in permittivity specification.", ValueError)

    return value


def subprocess_cmd(command):
    """Execute a (multi-line) shell command.

    Parameters
    ----------
    command : str
        Semicolon separated lines.
    """
    comm_lines = command.split(";")
    for line in comm_lines:
        comm_list = list(line.split())
        process = subprocess.run(
            comm_list, stdout=None, check=True, stdin=subprocess.DEVNULL
        )


def object_name(name_list, obj, prefix=""):
    """Return a name for the object that is unique within the names in a
    given list. The optional prefix is to be used if object.name is None.
    """
    if obj.name is not None:
        prefix = obj.name

    # plen = len(prefix)
    # entries_list = [n for n in name_list if n[]]
    # print(entries_list)
    # new_entry = prefix + f"_{len(entries_list) + 1}"
    # return new_entry

    count = 1
    name = prefix
    if obj.name is None:
        name += "_0"

    name_set = set(name_list)
    while name in name_set:
        name = prefix + "_" + str(count)
        count += 1

    return name


class UniqueNames(object):
    """ Class used for defining unique names for Monitors, Sources, Structures
    and materials."""

    def __init__(self, default_prefix=''):
        self.names = []
        self.names_set = set()
        self.prefixes = {}
        self.default_prefix = default_prefix
 
    def __getitem__(self, name_ind):
          return self.names[name_ind]

    def __repr__(self):
        return str(self.names)

    def __iter__(self):
        self.n = 0
        self.len = len(self.names)
        return self

    def __next__(self):
        if self.n < self.len:
            result = self.names[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def append(self, name):

        if name is None:
            name = self.default_prefix

        if name in self.prefixes.keys():
            if name in self.names_set:
                self.prefixes[name] += 1
                newname = f"{name}_{self.prefixes[name]}"
            else:
                # Handle the edge case of someone trying to add 'name_i' 
                # after 'name_i' has already been automatically added
                self.prefixes[name] = 1
                newname = name + "_1"
        else:
            self.prefixes[name] = 0
            newname = name

        # Make sure name is still unique
        while newname in self.names_set:
            self.prefixes[name] += 1
            newname = name + f"_{self.prefixes[name]}"

        self.names.append(newname)
        self.names_set.add(newname)

        return newname


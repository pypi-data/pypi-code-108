"""
Convenience function for importing a fqdn from a package.
(to hide the baroque nature of __import__).
"""

import sys
import os
import inspect


def dkimport(name):
    """Import and return the item specified by name:

       Usage::

           >>> item = dkimport('dk.dkimport.dkimport')
           >>> item.__name__
           'dkimport'

    """
    name = str(name)  # can't import unicode, or special chars..
    if name.startswith('/'):
        raise ValueError("Cannot import from implicit root.")
    # print("DKIMPORT:", name)
    if sys.version_info < (3, 0):  # pragma: nocover
        if '.' in name:
            package, item = name.rsplit('.', 1)
            tmp = __import__(package, {}, {}, [item], -1)
            return getattr(tmp, item)
        else:
            return __import__(name, {}, {}, [], -1)
    else:  # pragma: nocover
        if '.' in name:
            package, item = name.rsplit('.', 1)
            tmp = __import__(package, {}, {}, [item], 0)
            return getattr(tmp, item)
        else:
            return __import__(name, {}, {}, [], 0)
        # import importlib
        # return importlib.import_module(name)


def _true(_x):
    return True


def load_files_from(module_path, module_name, filefilter=None):
    """Load all .py files in module.
    """
    filefilter = filefilter or _true
    for fname in sorted(os.listdir(module_path)):
        valid_fname = fname.endswith('.py') and not fname.startswith('_')
        if valid_fname and filefilter(fname):
            name = os.path.splitext(fname)[0]
            yield dkimport(module_name + '.' + name)


def defined_symbols(module, attrfilter=None, itemfilter=None):
    """Return symbols that are defined in module.
    """
    attrfilter = attrfilter or _true
    itemfilter = itemfilter or _true
    for attr in dir(module):
        if attr.startswith('_'):
            continue
        if not attrfilter(attr):
            continue

        item = getattr(module, attr)
        if inspect.getmodule(item) == module and itemfilter(item):
            yield item


def dkimport_star(modname, **kw):
    """Import all names from module `modname`, similar to::

           from modname import *

       Available ``**kw`` arguments:

           filefilter      A function that receives a filename (with extension
                           but without path) that should return True if the
                           filename should be included.

       useful for modularly implementing functionality, yet making
       it dynamically available from the top namespace::

           ...path/cmds/a.py
               def a(): ...
           ...path/cmds/b.py
               def b(): ...
           ...path/cmds/c.py
               def c(): ...

           ...path/cmds/__init__.py
               from dk.dkimport import dkimport_star as _dki

               for _item in _dki('..path.cmds'):
                   if hasattr(_item, '__name__'):
                       globals()[_item.__name__] = _item

    """
    module_path, module_name = modname.rsplit('.', 1)
    parent_module = dkimport(module_path)
    parent_path = os.path.split(parent_module.__file__)[0]
    fpath = os.path.join(parent_path, module_name)
    symbols = []
    for m in load_files_from(fpath, modname, kw.get('filefilter')):
        for symbol in defined_symbols(m,
                                      kw.get('attrfilter'),
                                      kw.get('itemfilter')):
            symbols.append(symbol)

    return symbols


def dkimport_functions(modname, **kw):
    """Return all functions from all direct sub-modules of `modname`.
    """
    return dkimport_star(modname, itemfilter=inspect.isfunction, **kw)

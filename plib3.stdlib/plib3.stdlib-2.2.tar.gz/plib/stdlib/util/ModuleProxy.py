#!/usr/bin/env python3
"""
Module ModuleProxy
Sub-Package STDLIB.UTIL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ModuleProxy class. For examples
of intended use cases for this class, check out the
``main.py`` module in the PLIB3.GUI sub-package, or any
of a number of ``__init__.py`` modules in the PLIB3.IO
sub-packages. The docstrings and comments there give more
information.

One note about usage: whenever importing from a package
that uses this functionality, absolute imports should be
used. Using relative imports risks running afoul of the
name ambiguity between the object you want to import (a
class, usually) and the module it's defined in. Absolute
imports are "purer" anyway, so this is not viewed as a
bothersome restriction.
"""

import sys
import os
import glob
import types

from plib.stdlib.imp import import_from_module

__all__ = ('ModuleProxy',)


# Helper function for lazy loading of actual modules

def module_helper(pkgname, modname):
    
    def f():
        try:
            return import_from_module(
                '{}.{}'.format(pkgname, modname),
                modname
            )
        except:
            try:
                # Try retrieving modname from pkgname as an attribute
                # FIXME: why does this sometimes help? Nothing like
                # this was needed in Python 2, and the advertised
                # semantics of the above import_from_module call should
                # mean that if the below works, the above should have!
                return getattr(sys.modules.get(pkgname), modname)
            except:
                raise TypeError
    
    f.__name__ = "{}_helper".format(modname)
    return f


# Note that we subclass types.ModuleType in order to fool
# various introspection utilities (e.g., pydoc and the builtin
# 'help' command in the interpreter) into thinking ModuleProxy
# instances are actual modules. Among other things, this is
# necessary for the builtin 'help' command to properly display
# the info from the proxied module's docstring (setting the
# proxy's __doc__ to the actual module's __doc__ is *not*
# enough to do this by itself); note also that we don't
# override the constructor because various Python internals
# expect module objects to have a particular signature for
# the constructor; instead, we add the init_proxy method which
# must be called immediately on constructing the object to do
# the proxying magic

class ModuleProxy(types.ModuleType):
    
    def init_proxy(self, name, path, globals_dict, locals_dict,
                   names=None, excludes=None, autodiscover=True):
        
        self._excludes = excludes
        
        names = dict(names or {})
        excludes = set(excludes or [])
        
        if autodiscover:
            for pathname in path:
                for filename in glob.glob(os.path.join(pathname, "*.py")):
                    modname = os.path.splitext(os.path.basename(filename))[0]
                    if not self._exclude(modname, excludes):
                        names[modname] = module_helper(name, modname)
        
        self._names = names
        self._realized_names = []
        
        # Monkeypatch sys.modules with the proxy object (make
        # sure we store a reference to the real module first!)
        self._mod = sys.modules[name]
        sys.modules[name] = self
        
        # Pass-through module's docstring (this attribute name
        # appears in both so __getattr__ below won't handle it);
        # as noted above, this in itself isn't enough to make
        # the 'help' builtin work right, but it is a necessary
        # part of doing so
        self.__doc__ = self._mod.__doc__
    
    def __repr__(self):
        return "<proxy of module '{}' from '{}'>".format(
            self._mod.__name__, self._mod.__file__)
    
    def _exclude(self, name, excludes):
        # This allows customization of the exclusion algorithm; by
        # default we exclude names in the excludes set and private
        # names (ones that start with '_')
        return (name in excludes) or name.startswith('_')
    
    def _realize_name(self, name, value):
        setattr(self, name, value)  # so it gets retrieved without __getattr__
        self._realized_names.append(name)  # so __dir__ can see it
    
    not_proxied = object()
    
    def _get_name(self, name, module=None):
        names = self.__dict__['_names']
        result = names.get(name, self.not_proxied)
        if result is not self.not_proxied:
            
            if module is None:
                # This hack allows features like 'lazy importing' to work;
                # a callable names dict entry allows arbitrary (and possibly
                # expensive) processing to take place only when the attribute
                # is first accessed, instead of when the module is initially
                # imported. Also, since we store the result in our __dict__,
                # the expensive function won't get called again, so we are
                # essentially memoizing the result.
                try:
                    newresult = result()
                except TypeError:
                    pass
                else:
                    result = newresult
            
            else:
                # This can happen if the underlying sub-module was imported
                # before we got a chance to proxy it
                try:
                    newresult = getattr(module, name)
                except AttributeError:
                    # It wasn't a proxied name after all (or else it isn't
                    # being proxied our way)
                    result = self.not_proxied
                else:
                    result = newresult
        
        if (result is not self.not_proxied) and (name in names):
            assert name not in self._realized_names
            self._realize_name(name, result)
            del names[name]  # no need to track it any more
        
        return result
    
    not_in_real_module = object()
    
    def __getattr__(self, name):
        # Remember we need to return the real module's attributes!
        mod_result = getattr(self._mod, name, self.not_in_real_module)
        if mod_result is self.not_in_real_module:
            our_result = self._get_name(name)
            if our_result is self.not_proxied:
                raise AttributeError("{} object has no attribute {}".format(
                                     self, name))
            else:
                return our_result
        else:
            if isinstance(mod_result, types.ModuleType):
                # We might have gotten the underlying module for a proxied name
                our_result = self._get_name(name, mod_result)
                if (our_result is not self.not_proxied):
                    return our_result
            return mod_result
    
    def __dir__(self):
        return sorted(dir(self._mod) + self._realized_names + list(self._names.keys()))

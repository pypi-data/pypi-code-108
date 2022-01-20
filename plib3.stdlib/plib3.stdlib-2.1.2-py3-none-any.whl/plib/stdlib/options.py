#!/usr/bin/env python3
"""
Module OPTIONS -- Option Parser Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a convenience function for argument parsers,
to reduce the amount of work needed to make use of the argparse
library module. Instead of having to manually instantiate an
option parser, add options to it, then call its parsing method,
the parse_options function wraps it all into one package; you
give it a list of option parameters and arguments and it
returns the parsed (options, args) tuple. This also allows
adding extra functionality:

- Option dictionary: the options object (the first element of
  the 2-tuple returned by ``parse_options``) supports an
  immutable mapping interface, using the destination variable
  names passed in the option list as keys. This makes it
  easier to use the options to update other data structures
  in the program (see the gui-display.py example program for
  an illustration of this usage), as well as accessing the
  options directly as attributes of the options object.

- Argument sequence: the arguments object (the second element
  of the 2-tuple returned by ``parse_options``) supports a
  sequence interface; an argument's index in the sequence is
  equal to its index in the list of arguments passed to the
  ``parse_options`` function. This allows easy iteration over
  arguments, as well as accessing them by name directly as
  attributes of the arguments object.

The major pieces of the convenience function are also factored
out and provided as separate functions:

- ``prepare_specs``: returns canonicalized versions of option
  and argument lists. If you are using any of the other factored
  out functions below, it is recommended that you first use this
  one to prepare your option and/or argument lists; the other
  functions assume that the option and argument lists passed to
  them are canonicalized.

- ``update_parser``: takes an existing parser and adds options and
  arguments to it from the given lists.

- ``make_parser``: returns a parser from the given option list
  and argument list. Useful when you want to do further processing
  with the parser before invoking it (such as adding functionality
  not encapsulated in this module).

- ``invoke_parser``: returns the result of the given parser. Useful
  when you want an ``opts, args`` tuple from a parser that you have
  either constructed yourself, or received from ``make_parser`` and
  made enhancements to.

- ``make_objs``: returns an ``opts, args`` tuple from a parser
  result namespace using the given option list and argument list.
  Useful when you want to invoke the parser using a method not
  encapsulated in this module, but still use the added functionality
  of the option and argument objects it provides.
"""

import argparse

from plib.stdlib.coll import AttrDict, AttrList


def canonicalize_opt(opt):
    shortopt, longopt, kwargs = opt
    assert shortopt.startswith('-')
    assert longopt.startswith('--')
    kwargs = dict(kwargs)  # avoid mutating the original
    if 'dest' not in kwargs:
        kwargs['dest'] = longopt[2:].lower().replace('-', '_')
    return shortopt.lower(), longopt.lower(), kwargs


def canonicalize_opts(optlist):
    return [canonicalize_opt(opt) for opt in optlist]


def canonicalize_arg(arg):
    if isinstance(arg, str):
        argname, kwargs = arg, {}
    else:
        argname, kwargs = arg
    kwargs = dict(kwargs)  # avoid mutating the original
    if 'metavar' not in kwargs:
        kwargs['metavar'] = argname.upper()
    return argname.lower(), kwargs


def canonicalize_args(arglist):
    if isinstance(arglist, str):
        import warnings
        warnings.warn(
            "A single string as an argument definition is deprecated; use a one-element list instead.",
            DeprecationWarning
        )
        arglist = [arglist]
    return [canonicalize_arg(arg) for arg in arglist]


def prepare_specs(optlist=None, arglist=None):
    """Canonicalize option and argument spec lists.
    """
    
    optlist, arglist = optlist or (), arglist or ()
    
    optlist = canonicalize_opts(optlist)
    arglist = canonicalize_args(arglist)
    
    return optlist, arglist


def update_parser(parser, optlist=None, arglist=None):
    """Add given options and arguments to parser.
    """
    for shortopt, longopt, kwargs in optlist:
        parser.add_argument(shortopt, longopt, **kwargs)
    for argname, kwargs in arglist:
        parser.add_argument(argname, **kwargs)


def make_parser(optlist=None, arglist=None,
                description=None, epilog=None,
                add_help=True):
    """Return a parser with the given parameters.
    """
    
    parser = argparse.ArgumentParser(
        description=description, epilog=epilog,
        add_help=add_help)
    update_parser(parser, optlist, arglist)
    return parser


def optnames(optlist):
    return [optitem[2]['dest'] for optitem in optlist]


def argnames(arglist):
    return [argitem[0] for argitem in arglist]


def make_ns(names, items):
    ns = argparse.Namespace()
    for name in names:
        setattr(ns, name, getattr(items, name))
    return ns


def make_attrs(klass, keys, result):
    return klass(keys, make_ns(keys, result))


def make_objs(result, optlist=None, arglist=None):
    """Return an ``opts, args`` tuple from a parser result namespace.
    """
    
    opts = make_attrs(AttrDict, optnames(optlist), result)
    args = make_attrs(AttrList, argnames(arglist), result)
    return opts, args


def invoke_parser(parser, optlist=None, arglist=None,
                  args=None, ns=None, incremental=False):
    """Return the result from parser with the given parameters.
    """
    
    if incremental:
        result, remaining = parser.parse_known_args(args, ns)
    else:
        result = parser.parse_args(args, ns)
    
    opts, args = make_objs(result, optlist, arglist)
    
    if incremental:
        return opts, args, result, remaining
    return opts, args


def parse_options(optlist=None, arglist=None,
                  description=None, epilog=None,
                  args=None, ns=None, incremental=False,
                  add_help=True):
    """Convenience function for option and argument parsing.
    
    Adds each option in optlist and each argument in arglist to the
    parser and then return the parsing results.
    
    Parameters:
    
        - ``optlist``: a sequence of 3-tuples: short name, long name,
          dict of keyword arguments.
        
        - ``arglist``: either a sequence of strings which are interpreted
          as argument names, or a sequence of 2-tuples: argument name,
          dict of keyword arguments. The latter form is the "canonical"
          form into which the former will be converted; in that case, each
          2-tuple is then simply the arg name and a dict with a single
          key, 'metavar', mapped to the arg name as its value (note,
          though, that arg names are always lowercased and metavar names
          are always uppercased in this mode).
        
        - ``description``: to be printed at the top of the help message.
        
        - ``epilog``: to be printed at the end of the help message, after
          all argument descriptions.
        
        - ``args``: if present, the parser will parse this list of args
          instead of taking them from ``sys.argv``. Useful when incremental
          parsing is being used (see next item).
        
        - ``ns``: if present, the parser will add its results to this
          namespace instead of creating a new one.
        
        - ``incremental``: if true, the presence of unknown arguments does
          not cause an error; instead, the current result namespace and all
          remaining unparsed arguments are returned as the third and fourth
          elements of the return tuple.
    """
    
    optlist, arglist = prepare_specs(optlist, arglist)
    parser = make_parser(optlist, arglist, description, epilog, add_help)
    return invoke_parser(parser, optlist, arglist, args, ns, incremental)

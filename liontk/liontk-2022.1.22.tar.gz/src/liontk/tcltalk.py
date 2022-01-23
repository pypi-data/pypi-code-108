"""tcltalk.py  -- functions for talking with Tcl/Tk from Python

These are the core functions for communicating with Tcl via Python.

This module must be initialized with a call to setup().


If you want to understand Tcl quoting, I recommend reading:

  TIP 407:
    The String Representation of Tcl Lists: the Gory Details

  https://core.tcl-lang.org/tips/doc/trunk/tip/407.md


quote(s)  -- quote a string form for Tcl, that doesn't evaluate
encase(s)  -- create a string form for Tcl, that DOES evaluate
subst(s)  -- substitute a tk string; ex: $top.foo to x.foo
peek(var)  -- peek at the value of a Tk variable
poke(var, s)  -- poke a value into a string
tclexec(tclcode)  -- execute code in Tcl directly
mkcmd(tkname, fn)  --- bind a command from Tcl to Python
"""

import tkinter as tk

from liontk.symbols import *


# Global Root & Functions -- Tk Fundamental

g = {REQUEST: None,
     RESULT: None}


root = None  # setup()
call = None  # setup()
createcommand = None  # setup()
tkeval = None  # setup()

def setup():
    global root, call, createcommand, tkeval
    root = tk.Tk()
    call = root.tk.call  # receives a list of literal strings
    createcommand = root.tk.createcommand  # literal key?
    tkeval = root.tk.eval  # direct; handled as a single string by tk


# Functions -- primary interfaces: peek, poke, tclexec, & mkcmd; also: quote

def quote(s):
    """Generate a string form for Tcl, that doesn't evaluate.
    
    Use poke & peek to avoid this.  But if you're generating code, you need it.

    This should work because the special characters are:
      "  -- covered here
      $  -- covered here
      [  -- covered here
      {  -- not special when not the first character, so not needed
            (the first character returned here will ALWAYS be '"')
      \\  -- covered here
      white space  -- not included within double-quotes, so not needed
    """
    return '"' + s.replace("\\", "\\\\").replace('[', '\\[').replace('$', '\\$').replace('"', '\\"') + '"'


def encase(s):
    """Generate a string form for Tcl, that DOES evaluate."""
    return '"' + s.replace('"', '\\"') + '"'


def subst(tkname):
    """Perform substitutions on a tkname.
    
    This is most commonly used to resolve a full path.
    
    For example, "$top.foo" can substitute to "$tag1.foo".
    """
    return tkeval('subst '+tkname)


def peek(tkname):
    """Peek a value.
    
    For example, peek("w") -> ".settings" (or whatever)
    """
    return tkeval('set '+tkname)


def poke(tkname, s):
    """Poke a string value literally into tk.
    
    Does NOT perform $-substitutions.
    If you want substitutions, us the form: poke(tkname, subst(s))
    """
    call('set', tkname, s)  # LITERAL


def tclexec(tcl_code):
    """Run tcl code.  Returns the response from Tcl."""
    g[REQUEST] = tcl_code
    g[RESULT] = tkeval(tcl_code)
    return g[RESULT]


def mkcmd(tkname, fn):
    """Bind a tk command to a function"""
    createcommand(tkname, fn)


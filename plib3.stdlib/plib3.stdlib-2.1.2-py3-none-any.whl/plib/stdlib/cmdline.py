#!/usr/bin/env python3
"""
Module CMDLINE -- Tools for Command-Line Scripts
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

This module contains tools for building and running command-line
scripts. There are two public functions available:

function ``setup_history`` -- set up command line history
handling. Typical usage is to import this function and call it
in your .pystartup file.

function ``run_shell`` -- run an interactive Python shell with
a desired environment already set up.
"""


def setup_history(history_path=None):
    """Set up command line history handling.
    
    History info is stored in the file pointed to by the
    ``history_path`` parameter, if present; otherwise it
    defaults to ``.pyhistory`` in the user's home directory.
    """
    
    import os
    import atexit
    import readline
    
    if not history_path:
        history_path = os.path.expanduser("~/.pyhistory")
    
    def save_history():
        import readline
        readline.write_history_file(history_path)
    
    if os.path.exists(history_path):
        readline.read_history_file(history_path)
    
    atexit.register(save_history)


def run_shell(disable_history=False, history_path=None, frame_level=1):
    """Run an interactive shell with a desired environment set up.
    
    The shell works like the standard Python interpreter prompt,
    but whatever local variables are in the caller's scope will
    be visible in the shell. The simplest use case is calling
    this function from the top level of a script (i.e., in the
    ``if __name__ == '__main__':`` clause); in this case all of
    the globals in the script's source file are visible (because
    at module level the "locals" are the module globals).
    
    The shell will set up command history handling the same way
    it is set up for the standard Python shell, using the file
    at ``history_path`` to store the history (this defaults to
    the file ``.pyhistory`` in the current directory). If history
    handling is not desired, set ``disable_history`` to ``True``.
    
    The ``frame_level`` parameter lets you compensate for extra
    levels in the call stack when this function is invoked. For
    example, if you wrap this function in another one that does
    some parameter parsing, but you want the globals in the module
    as a whole to be visible, you would pass ``frame_level=2`` to
    tell this function to walk one extra level up the stack (past
    the wrapper function to the module).
    """
    
    import sys
    import code
    if not disable_history:
        setup_history(history_path)
    code.interact(local=sys._getframe(frame_level).f_locals)

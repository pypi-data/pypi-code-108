"""
:mod:`moke.util`
================

Utility functions for creating and interacting with command-line applications.

"""
__all__ = ["chk", "chk_exist", "chk_exit", "chk_pth", "chk_type", "chks",
           "istrue", "inp_dir", "inp_file", "log", "log_run", "mkdir",
           "out_dir", "out_file", "out_pth", "path", "run_app", "sh",
           "tmp_file"]

import os
import sys
import logging
from .path import path
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE


def chk_exit(status, cargo=None, always=False):
    """
    Kills Python with a status and error message.

    Arguments:

      - status(``int``) Exist status.
      - cargo(``str``) Error message [default: ``None``].
      - always(``bool``) Exit even if status is ``0`` [default: ``True``].

    """
    if status or always:
        if cargo:
            log(cargo, logging.ERROR)
        sys.exit(status)
    return cargo

def log(msg, level=None, logger=None):
    """
    Universal logging function.
    
    Arguments:
    
      - msg(``str``) message to log.
      - level(``int``) logging level [default: INFO].
     
    """
    if not logger:
        logger = logging.getLogger("moke")
    logger.log(level or logging.DEFAULT, msg)
    
def run_app(cmd, args=None, stdin=None, **kwargs):
    """
    A simple wrapper around ``subprocess.Popen`` executes a command-line
    application with the given arguments and returns a 3-tuple of
    ``(returncode, stdout, stderr)``.
    
    Arguments:
    
      - app (``str``) The name of the application to run.
      - args (``sequence``) [default: ``None``] A sequence of arguments to the
        program.
      - stdin (``file``) A file-like object open for reading.
    
    Additional keyworded arguments are passed to the ``subprocess.Popen``
    constructor.
    
    """
    kwargs['stdout'] = kwargs.get('stdout', None) or PIPE
    kwargs['stderr'] = kwargs.get('stderr', None) or PIPE
    if args is not None:
        args.insert(0, cmd)
        app = Popen(args=args, stdin=stdin, **kwargs)
    else:
        kwargs["shell"] = True
        app = Popen(cmd, stdin=stdin, **kwargs)
    stdout, stderr = app.communicate(stdin)
    code = app.wait()
    return (code, stdout, stderr, " ".join(args or (cmd,)))


def log_run(code_stdout_stderr_cmd, pfx=""):
    code, stdout, stderr, cmd = code_stdout_stderr_cmd
    so = ("%sshell[%s]: %s") % (pfx, code, cmd)
    if not code:
        log(so, level=logging.DEFAULT)
    else:
        log(so, level=logging.ERROR)
    return code

def sh(command, **kwargs):
    """
    Executes command-line in the shell. No ``stdin``, ``stdout`` and ``stderr``
    go to ``/dev/null`` and the command is executed via the default shell.
    Additional keyworded arguments are passed to ``Popen``.
    
    Arguments:
    
      - command(``str`` or sequence of ``str``) This command line will be executed.
        See the documentation for "args" in ``subprocess.Popen``.
    
    """
    NULL = open(os.devnull, 'w')
    app = Popen(command, stdin=None, stdout=NULL, stderr=NULL, \
                                        shell=True, **kwargs)
    app.communicate()
    code = app.wait()
    return code

def tmp_file(filepath=None, overwrite=False, suffix=None):
    """
    Creates a temporary file and returns a file handle. If "filepath" is given
    it will be created or overwritten if overwrite is ``True``, else a temporary
    file will be created. The name of the file is accessible from the "name"
    attribute of the file handle, the file ceases to exist if it is closed or
    eventually disappears if the handle garbage collected.
    
    Arguments:
    
      - filepath(``str``) [default: ``None``] Path to the file.
      - overwrite(``bool``) [default: ``False``] Should the destination be
        overwritten if it exists? (ignored if "filepath" is ``None``)
    
    """
    suffix = (suffix or "")
    if filepath:
        if os.path.exists(filepath) and not overwrite:
            raise ValueError('The path: %s exists!' % filepath)
        fh = open(filepath, 'w+')
    else:
        fh = NamedTemporaryFile(mode='w+', suffix=suffix)
    return fh

def istrue(cond, msg):
    if cond:
        return 0, ""
    else:
        return 1, msg

def chk_pth(pth):
    if not isinstance(pth, path):
        return 1, "not a valid path: %s" % pth
    return 0, pth

def chk_exist(pth, should_exist):
    notpath, pth = chk_pth(pth)
    if notpath:
        return 1, pth
    if should_exist and not pth.exists():
        return 1, "missing path: %s" % pth
    elif not should_exist and pth.exists():
        return 1, "blocking path: %s" % pth
    return 0, pth

def chk_type(pth, should_dir):
    notexist, pth = chk_exist(pth, True)
    if notexist:
        return 1, pth
    if should_dir and not pth.isdir():
        return 1, "path is not a directory: %s" % pth
    elif not should_dir and pth.isdir():
        return 1, "path is not a file: %s" % pth
    return 0, pth

def inp_dir(pth):
    return chk_type(pth, True)

def inp_file(pth):
    return chk_type(pth, False)

def out_dir(pth):
    return chk_exist(pth, False)

def out_file(pth):
    return chk_exist(pth, False)

def out_pth(pth):
    t1, err1 = chk_exist(pth, True)
    if t1:
        return t1, err1
    t2, err2 = chk_type(pth, True)
    if t2:
        return t2, err2
    return 0, pth

def chks(checks):
    checks = tuple(checks)
    errors = [check[1] for check in checks if check[0]]
    if errors:
        sys.exit("\n".join(errors))
    return [check[1].abspath() for check in checks]

def chk(check):
    return chks((check,))[0]

def mkdir(path):
    """
    Creates a directory and is silent if it already exists.
    
    Arguments:
    
      - path(``path``) A path object.
    
    """
    try:
        path.mkdir_p()
    except OSError as _:
        path.makedirs_p()

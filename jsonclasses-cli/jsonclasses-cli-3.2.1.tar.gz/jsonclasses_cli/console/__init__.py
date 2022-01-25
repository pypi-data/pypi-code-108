from pathlib import Path
from code import interact
from sys import path
from os.path import splitext
from importlib import import_module
from jsonclasses.isjsonclass import isjsonclass


def console(dest: Path, app_file: Path):
    path.append(str(dest))
    result = import_module(splitext(app_file.name)[0], str(dest)).__dict__
    locals = {}
    for (k, v) in result.items():
        if isjsonclass(v):
            locals[k] = v
    models = ", ".join(list(locals.keys()))
    interact(banner=f"JSONClasses Console\nAvailable Models: {models}", local=locals)

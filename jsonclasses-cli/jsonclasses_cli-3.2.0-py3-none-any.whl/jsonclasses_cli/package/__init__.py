from typing import Literal
from pathlib import Path
from sys import path
from importlib import import_module
from os.path import splitext
from unittest.mock import patch
from jsonclasses.cgraph import CGraph
from .kotlin import kotlin
from .swift import swift
from .ts import ts



def package(dest: Path, app_file: Path, lang: Literal['ts', 'swift', 'kotlin'], cgraph_name: str = 'default', silent: bool = False):
    path.append(str(app_file.parent))
    import_module(splitext(app_file.name)[0], str(app_file.parent)).__dict__
    cgraph = CGraph(cgraph_name)
    match lang:
        case 'swift':
            swift(dest, cgraph, silent)
        case 'kotlin':
            kotlin(dest, cgraph, silent)
        case 'ts':
            ts(dest, cgraph, silent)

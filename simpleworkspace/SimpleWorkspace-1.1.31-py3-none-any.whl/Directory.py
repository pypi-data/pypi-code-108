from typing import Callable as _Callable
import SimpleWorkspace as _sw
from queue import Queue as _Queue
import re as _re
import os as _os
import shutil as _shutil


def Create(path: str):
    _os.makedirs(path, exist_ok=True)

def ListFiles(searchDir: str, callback: _Callable[[str], None] = None, includeDirs=True, includeFilter=None, satisfiedCondition: _Callable[[str], bool] = None) -> (list[str] | None):
    """
    includeFilter:
        options takes a regex which searches full path of each file, if anyone matches a callback is called. Is not case sensitive
    satisfiedCondition:
        takes a callback that returns a bool, if it returns true, no more search is performed
    :returns
        if no callback is given, a list of all found filepaths will be returned\n
        otherwise None
    """

    if not _os.path.exists(searchDir):
        return

    # only returned if callback was not given
    allEntries = [] if (callback is None) else None

    folders = _Queue()
    folders.put(searchDir)
    while folders.qsize() != 0:
        currentFolder = folders.get()
        try:
            currentFiles = _os.listdir(currentFolder)
            for filePath in currentFiles:
                filePath = _os.path.join(currentFolder, filePath)
                pathMatchesIncludeFilter = includeFilter == None or _re.search(includeFilter, filePath, _re.IGNORECASE)
                if _os.path.isfile(filePath):
                    if pathMatchesIncludeFilter:
                        if callback != None:
                            callback(filePath)
                        else:
                            allEntries.append(filePath)
                else:
                    if includeDirs:
                        if pathMatchesIncludeFilter:
                            if callback != None:
                                callback(filePath)
                            else:
                                allEntries.append(filePath)
                    folders.put(filePath)
                if satisfiedCondition != None and satisfiedCondition(filePath):
                    return
        except Exception as e:
            pass
    return allEntries

def Remove(path:str) -> None:
    _shutil.rmtree(path, ignore_errors=True)
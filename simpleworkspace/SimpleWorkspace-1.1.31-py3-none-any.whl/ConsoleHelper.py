import os as _os
import SimpleWorkspace as _sw
import shlex as _shlex

def LevelPrint(level, msg=None):
    for i in range(level):
        print("    ", end="", flush=True)
    if msg != None:
        print(msg)


def LevelInput(level, msg=""):
    LevelPrint(level)
    return input(msg)


def AnyKeyDialog(msg=""):
    if msg != "":
        msg += " - "
    msg += "Press enter to continue..."
    input(msg)


def ClearConsoleWindow():
    _os.system("cls" if _os.name == "nt" else "clear")
    return


def Print_SelectFileDialog(message="Enter File Path",printlevel=0) -> list[str]|None:
    LevelPrint(printlevel, f"-{message} (Separate multiple paths with space)")
    filepathString = LevelInput(printlevel, "-")
    filepaths = _shlex.split(filepathString)
    if(len(filepaths) == 0):
        return None
    return filepaths


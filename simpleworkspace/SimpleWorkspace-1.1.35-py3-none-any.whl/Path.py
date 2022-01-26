import SimpleWorkspace.ExtLibs.appdirs as _appdirs
import SimpleWorkspace as _sw
import os as _os


def FindEmptySpot(filepath: str):
    fileContainer = _sw.File.FileContainer(filepath)
    TmpPath = fileContainer.tail + fileContainer.filename + fileContainer.fileEnding
    i = 1
    while _os.path.exists(TmpPath) == True:
        TmpPath = fileContainer.tail + fileContainer.filename + "(" + str(i) + ")" + fileContainer.fileEnding
        i += 1
    return TmpPath

def GetAppdataPath(appName=None, companyName=None):
    """
    Retrieves roaming Appdata folder.\n
    no arguments        -> %appdata%/\n
    appName only        -> %appdata%/appname\n
    appname and company -> %appdata%/appname/companyName\n
    """
    return _appdirs.user_data_dir(appName, companyName, roaming=True)

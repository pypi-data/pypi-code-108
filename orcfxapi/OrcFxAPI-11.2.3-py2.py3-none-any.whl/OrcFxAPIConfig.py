import sys
import os
import os.path
import ctypes

_isPy3k = sys.version_info[0] >= 3
_libPathName = '_OrcFxAPIlib'
_libHandleName = '_OrcFxAPIlibHandle'

if _isPy3k:
    import builtins
    import winreg
else:
    import __builtin__ as builtins
    import _winreg as winreg

_libPath = None
_libHandle = None


def getLibPath():
    result = _libPath
    if result is not None:
        return result

    result = os.environ.get(_libPathName, None)
    if result is not None:
        return result

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'Software\\Orcina\\OrcaFlex\\Installation Directory', 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY) as key:
            installationDirectory = winreg.QueryValueEx(key, 'Normal')[0]
    except BaseException:  # registry key will not exist if OrcaFlex is not installed
        raise Exception('OrcaFlex not found')
    is64bit = ctypes.sizeof(ctypes.c_voidp) == 8
    if is64bit:
        platform = 'Win64'
    else:
        platform = 'Win32'
    return os.path.join(installationDirectory, 'OrcFxAPI', platform, 'OrcFxAPI.dll')


def setLibPath(value, childProcessInherit=False):
    global _libPath
    _libPath = os.path.abspath(value)
    if childProcessInherit:
        os.environ[_libPathName] = _libPath


def getLibHandle():
    result = _libHandle
    if result is None:
        result = getattr(builtins, _libHandleName, None)
    return result


def setLibHandle(value):
    global _libHandle
    _libHandle = value


def lib():
    libHandle = getLibHandle()
    if libHandle:
        return ctypes.WinDLL('', handle=libHandle)
    return ctypes.WinDLL(getLibPath())
